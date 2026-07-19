"""RiskLens secure API layer for Week 4 and Week 5.

Features:
- FastAPI API layer
- Swagger Authorize button with HTTP Bearer auth
- JWT bearer authentication
- Constant-time credential comparison
- Request body limit
- Basic in-memory rate limiting
- Basic brute-force login lockout
- Correlation/request IDs
- Structured audit logging
- Singleton DB + RAG pipeline using lifespan
- Strong security headers
- JSON and Markdown report generation

Production notes:
- Use Redis/API Gateway/NGINX/Cloudflare for production rate limiting.
- Use TLS at reverse proxy/API gateway.
- Use OAuth/OIDC provider for production identity.
- Use WAF/DDoS protection at cloud/network edge.
"""

from __future__ import annotations

import asyncio
import hmac
import logging
import os
import time
import uuid
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

import jwt
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field

from rag_pipeline import RAGErrorResponse, RiskLensRAGPipeline
from report_generator import generate_compliance_report, report_to_markdown
from risklens_db import SecureComplianceDatabase, TechnicalFindingInput


# ==========================================
# LOGGING
# ==========================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("risklens_api")
audit_logger = logging.getLogger("risklens_audit")


# ==========================================
# CONFIG
# ==========================================

APP_NAME = "RiskLens Compliance API"
APP_VERSION = "1.0.0"

JWT_ALGORITHM = "HS256"
JWT_ISSUER = "risklens-api"
JWT_AUDIENCE = "risklens-client"
JWT_EXPIRY_MINUTES = 30

MAX_BODY_BYTES = 32_000
REQUEST_TIMEOUT_SECONDS = 15

RATE_LIMIT_REQUESTS = 30
RATE_LIMIT_WINDOW_SECONDS = 60

LOGIN_FAILURE_LIMIT = 5
LOGIN_LOCKOUT_SECONDS = 300

bearer_scheme = HTTPBearer(auto_error=False)


# ==========================================
# APP STATE
# ==========================================

class AppState:
    db: SecureComplianceDatabase | None = None
    pipeline: RiskLensRAGPipeline | None = None


state_container = AppState()


# ==========================================
# MODELS
# ==========================================

class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8, max_length=200)


class TokenResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in_seconds: int


class MappingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vulnerability_title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    severity: Literal["Critical", "High", "Medium", "Low"] = "Medium"
    cve: str | None = Field(default=None, max_length=50)
    framework_filter: Literal["NIST", "CIS", "ISO27001", "OTHER"] | None = None
    n_results: int = Field(default=3, ge=1, le=5)


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    service: str
    version: str


# ==========================================
# HELPERS
# ==========================================

def get_required_env(name: str, min_length: int = 1) -> str:
    value = os.getenv(name, "").strip()

    if len(value) < min_length:
        raise RuntimeError(f"{name} must be configured.")

    return value


def get_jwt_secret() -> str:
    return get_required_env("RISKLENS_JWT_SECRET", min_length=32)


def safe_client_ip(request: Request) -> str:
    if request.client and request.client.host:
        return request.client.host

    return "unknown"


def audit_event(
    *,
    event: str,
    request_id: str,
    client_ip: str,
    subject: str | None = None,
    status_value: str = "unknown",
) -> None:
    """Structured audit log without sensitive payloads."""

    audit_logger.info(
        "event=%s request_id=%s client_ip=%s subject=%s status=%s",
        event,
        request_id,
        client_ip,
        subject or "anonymous",
        status_value,
    )


def constant_time_equal(left: str, right: str) -> bool:
    return hmac.compare_digest(left.encode("utf-8"), right.encode("utf-8"))


# ==========================================
# RATE LIMITING + LOGIN LOCKOUT
# ==========================================

class SlidingWindowRateLimiter:
    """Basic in-memory rate limiter.

    Good for local prototype.
    Production should use Redis, API Gateway, NGINX, or Cloudflare.
    """

    def __init__(self, limit: int, window_seconds: int) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time.time()
        bucket = self.requests[key]

        while bucket and now - bucket[0] > self.window_seconds:
            bucket.popleft()

        if len(bucket) >= self.limit:
            return False

        bucket.append(now)
        return True


class LoginLockout:
    """Basic in-memory brute-force protection for login."""

    def __init__(self, failure_limit: int, lockout_seconds: int) -> None:
        self.failure_limit = failure_limit
        self.lockout_seconds = lockout_seconds
        self.failures: dict[str, list[float]] = defaultdict(list)
        self.locked_until: dict[str, float] = {}

    def is_locked(self, key: str) -> bool:
        locked_until = self.locked_until.get(key, 0)
        return time.time() < locked_until

    def record_failure(self, key: str) -> None:
        now = time.time()
        recent_failures = [
            timestamp
            for timestamp in self.failures[key]
            if now - timestamp <= self.lockout_seconds
        ]

        recent_failures.append(now)
        self.failures[key] = recent_failures

        if len(recent_failures) >= self.failure_limit:
            self.locked_until[key] = now + self.lockout_seconds

    def record_success(self, key: str) -> None:
        self.failures.pop(key, None)
        self.locked_until.pop(key, None)


rate_limiter = SlidingWindowRateLimiter(
    limit=RATE_LIMIT_REQUESTS,
    window_seconds=RATE_LIMIT_WINDOW_SECONDS,
)

login_lockout = LoginLockout(
    failure_limit=LOGIN_FAILURE_LIMIT,
    lockout_seconds=LOGIN_LOCKOUT_SECONDS,
)


# ==========================================
# JWT
# ==========================================

def create_access_token(subject: str) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=JWT_EXPIRY_MINUTES)).timestamp()),
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "jti": str(uuid.uuid4()),
    }

    return jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALGORITHM)


def verify_bearer_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any]:
    request_id = getattr(request.state, "request_id", "unknown")
    client_ip = safe_client_ip(request)

    if credentials is None or credentials.scheme.lower() != "bearer":
        audit_event(
            event="auth_missing_token",
            request_id=request_id,
            client_ip=client_ip,
            status_value="blocked",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token.",
        )

    token = credentials.credentials.strip()

    try:
        payload = jwt.decode(
            token,
            get_jwt_secret(),
            algorithms=[JWT_ALGORITHM],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE,
        )
    except jwt.PyJWTError:
        audit_event(
            event="auth_invalid_token",
            request_id=request_id,
            client_ip=client_ip,
            status_value="blocked",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    return payload


# ==========================================
# DEPENDENCIES
# ==========================================

def get_pipeline() -> RiskLensRAGPipeline:
    if state_container.pipeline is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Pipeline is not initialized.",
        )

    return state_container.pipeline


# ==========================================
# LIFESPAN
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting RiskLens API lifespan.")

    db = SecureComplianceDatabase()
    pipeline = RiskLensRAGPipeline(db=db)

    state_container.db = db
    state_container.pipeline = pipeline

    logger.info("RiskLens DB and RAG pipeline initialized.")

    yield

    logger.info("Shutting down RiskLens API lifespan.")
    state_container.pipeline = None
    state_container.db = None


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url=None,
)


# ==========================================
# CORS
# ==========================================

allowed_origins = [
    origin.strip()
    for origin in os.getenv("RISKLENS_ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)


# ==========================================
# SECURITY MIDDLEWARE
# ==========================================

@app.middleware("http")
async def security_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id

    client_ip = safe_client_ip(request)

    content_length = request.headers.get("content-length")

    if content_length:
        try:
            body_size = int(content_length)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Content-Length header.",
            )

        if body_size > MAX_BODY_BYTES:
            audit_event(
                event="request_body_too_large",
                request_id=request_id,
                client_ip=client_ip,
                status_value="blocked",
            )
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Request body too large.",
            )

    if not rate_limiter.allow(client_ip):
        audit_event(
            event="rate_limit_exceeded",
            request_id=request_id,
            client_ip=client_ip,
            status_value="blocked",
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded.",
        )

    try:
        response: Response = await asyncio.wait_for(
            call_next(request),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        audit_event(
            event="request_timeout",
            request_id=request_id,
            client_ip=client_ip,
            status_value="blocked",
        )
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Request timed out.",
        )

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data: https://fastapi.tiangolo.com; "
        "font-src 'self' data: https://cdn.jsdelivr.net; "
        "connect-src 'self'; "
        "frame-ancestors 'none';"
    )
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response


# ==========================================
# ROUTES
# ==========================================

@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=APP_NAME,
        version=APP_VERSION,
    )


@app.post("/auth/token", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request) -> TokenResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    client_ip = safe_client_ip(request)
    lockout_key = f"{client_ip}:{payload.username}"

    if login_lockout.is_locked(lockout_key):
        audit_event(
            event="login_locked",
            request_id=request_id,
            client_ip=client_ip,
            subject=payload.username,
            status_value="blocked",
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Try again later.",
        )

    expected_username = get_required_env("RISKLENS_API_USERNAME")
    expected_password = get_required_env("RISKLENS_API_PASSWORD", min_length=8)

    valid_username = constant_time_equal(payload.username, expected_username)
    valid_password = constant_time_equal(payload.password, expected_password)

    if not (valid_username and valid_password):
        login_lockout.record_failure(lockout_key)
        audit_event(
            event="login_failed",
            request_id=request_id,
            client_ip=client_ip,
            subject=payload.username,
            status_value="blocked",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )

    login_lockout.record_success(lockout_key)

    audit_event(
        event="login_success",
        request_id=request_id,
        client_ip=client_ip,
        subject=payload.username,
        status_value="success",
    )

    token = create_access_token(payload.username)

    return TokenResponse(
        access_token=token,
        expires_in_seconds=JWT_EXPIRY_MINUTES * 60,
    )


@app.post("/map")
def map_compliance(
    payload: MappingRequest,
    request: Request,
    token_payload: dict[str, Any] = Depends(verify_bearer_token),
    pipeline: RiskLensRAGPipeline = Depends(get_pipeline),
) -> dict[str, Any]:
    request_id = getattr(request.state, "request_id", "unknown")
    client_ip = safe_client_ip(request)
    subject = str(token_payload.get("sub", "unknown"))

    finding = TechnicalFindingInput(
        vulnerability_title=payload.vulnerability_title,
        description=payload.description,
        severity=payload.severity,
        cve=payload.cve,
    )

    response = pipeline.map_compliance_safe(
        finding=finding,
        n_results=payload.n_results,
        framework_filter=payload.framework_filter,
    )

    if isinstance(response, RAGErrorResponse):
        audit_event(
            event="mapping_failed",
            request_id=request_id,
            client_ip=client_ip,
            subject=subject,
            status_value=response.error_type,
        )
        raise HTTPException(status_code=400, detail=response.model_dump())

    audit_event(
        event="mapping_success",
        request_id=request_id,
        client_ip=client_ip,
        subject=subject,
        status_value="success",
    )

    return response.model_dump()


@app.post("/report/json")
def generate_json_report(
    payload: MappingRequest,
    request: Request,
    token_payload: dict[str, Any] = Depends(verify_bearer_token),
    pipeline: RiskLensRAGPipeline = Depends(get_pipeline),
) -> dict[str, Any]:
    request_id = getattr(request.state, "request_id", "unknown")
    client_ip = safe_client_ip(request)
    subject = str(token_payload.get("sub", "unknown"))

    finding = TechnicalFindingInput(
        vulnerability_title=payload.vulnerability_title,
        description=payload.description,
        severity=payload.severity,
        cve=payload.cve,
    )

    response = pipeline.map_compliance_safe(
        finding=finding,
        n_results=payload.n_results,
        framework_filter=payload.framework_filter,
    )

    if isinstance(response, RAGErrorResponse):
        audit_event(
            event="report_json_failed",
            request_id=request_id,
            client_ip=client_ip,
            subject=subject,
            status_value=response.error_type,
        )
        raise HTTPException(status_code=400, detail=response.model_dump())

    report = generate_compliance_report(response)

    audit_event(
        event="report_json_success",
        request_id=request_id,
        client_ip=client_ip,
        subject=subject,
        status_value="success",
    )

    return report.model_dump()


@app.post("/report/markdown")
def generate_markdown_report(
    payload: MappingRequest,
    request: Request,
    token_payload: dict[str, Any] = Depends(verify_bearer_token),
    pipeline: RiskLensRAGPipeline = Depends(get_pipeline),
) -> dict[str, str]:
    request_id = getattr(request.state, "request_id", "unknown")
    client_ip = safe_client_ip(request)
    subject = str(token_payload.get("sub", "unknown"))

    finding = TechnicalFindingInput(
        vulnerability_title=payload.vulnerability_title,
        description=payload.description,
        severity=payload.severity,
        cve=payload.cve,
    )

    response = pipeline.map_compliance_safe(
        finding=finding,
        n_results=payload.n_results,
        framework_filter=payload.framework_filter,
    )

    if isinstance(response, RAGErrorResponse):
        audit_event(
            event="report_markdown_failed",
            request_id=request_id,
            client_ip=client_ip,
            subject=subject,
            status_value=response.error_type,
        )
        raise HTTPException(status_code=400, detail=response.model_dump())

    report = generate_compliance_report(response)

    audit_event(
        event="report_markdown_success",
        request_id=request_id,
        client_ip=client_ip,
        subject=subject,
        status_value="success",
    )

    return {"markdown": report_to_markdown(report)}