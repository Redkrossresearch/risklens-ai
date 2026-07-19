"""Secure local ChromaDB service for the RiskLens prototype.

For Week 1 / local demo:
- Uses environment secret instead of hardcoded token
- Validates structured technical findings
- Uses constant-time token comparison
- Limits result count
- Handles ChromaDB errors safely
- Supports metadata from both seed data and ingested documents

For production:
- Put this behind an API layer with HTTPS, rate limiting, audit logs,
  token rotation, and proper user/service authentication.
"""

from __future__ import annotations

import hmac
import logging
import os
from pathlib import Path
from typing import Any, Literal

import chromadb
from pydantic import BaseModel, ConfigDict, Field


# ==========================================
# LOGGING
# ==========================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("risklens_db")


# ==========================================
# CONFIG
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "compliance_db"

COLLECTION_NAME = "frameworks"

MIN_SECRET_LENGTH = 32
MAX_QUERY_LENGTH = 1500
MAX_RESULTS_LIMIT = 10


# ==========================================
# DATA MODELS
# ==========================================

class TechnicalFindingInput(BaseModel):
    """Validated input received from parser/backend."""

    model_config = ConfigDict(extra="forbid")

    vulnerability_title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    severity: Literal["Critical", "High", "Medium", "Low"] = "Medium"
    cve: str | None = Field(default=None, max_length=50)


class ComplianceMatchSchema(BaseModel):
    """Safe response format returned to backend."""

    model_config = ConfigDict(extra="forbid")

    matched_rule: str
    framework: str
    control_id: str
    source_file: str | None = None
    page: int | None = None
    distance: float | None = None


# ==========================================
# SECURITY HELPERS
# ==========================================

def load_shared_secret() -> str:
    """Load secret from environment variable, not from source code."""

    secret = os.getenv("RISKLENS_SHARED_SECRET", "").strip()

    if len(secret) < MIN_SECRET_LENGTH:
        raise RuntimeError(
            f"RISKLENS_SHARED_SECRET must be configured with at least "
            f"{MIN_SECRET_LENGTH} characters."
        )

    return secret


def verify_access(user_token: str, expected_secret: str) -> bool:
    """Validate token using constant-time comparison."""

    if not isinstance(user_token, str):
        return False

    user_token = user_token.strip()

    if not user_token:
        return False

    return hmac.compare_digest(user_token, expected_secret)


def normalize_query_text(text: str) -> str:
    """Normalize query text without destroying useful compliance text."""

    if not isinstance(text, str):
        raise TypeError("Query must be text.")

    normalized = " ".join(text.split())

    if not normalized:
        raise ValueError("Query cannot be empty.")

    if len(normalized) > MAX_QUERY_LENGTH:
        raise ValueError(f"Query cannot exceed {MAX_QUERY_LENGTH} characters.")

    return normalized


def build_query_text(finding: TechnicalFindingInput) -> str:
    """Create semantic query text from structured finding."""

    query_text = (
        f"Vulnerability Title: {finding.vulnerability_title}\n"
        f"Severity: {finding.severity}\n"
        f"Description: {finding.description}\n"
        f"CVE: {finding.cve or 'N/A'}"
    )

    return normalize_query_text(query_text)


def safe_metadata_value(metadata: dict[str, Any], *keys: str, default: str = "N/A") -> str:
    """Read first available metadata key safely."""

    for key in keys:
        value = metadata.get(key)
        if value is not None and str(value).strip():
            return str(value)

    return default


# ==========================================
# DATABASE SERVICE
# ==========================================

class SecureComplianceDatabase:
    """Authenticated query layer around local ChromaDB."""

    def __init__(
        self,
        db_path: str | Path = DATABASE_PATH,
        *,
        shared_secret: str | None = None,
    ) -> None:
        self._shared_secret = shared_secret or load_shared_secret()

        self.client = chromadb.PersistentClient(path=str(db_path))

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "RiskLens compliance framework controls"},
        )

        self._initialize_sample_data()

        logger.info("SecureComplianceDatabase initialized.")

    def _initialize_sample_data(self) -> None:
        """Add fallback starter controls only if database is empty."""

        if self.collection.count() > 0:
            return

        self.collection.add(
            documents=[
                "ISO 27001 A.9.1.1: Access control policy requirement to restrict unauthorized user access.",
                "NIST CSF PR.AC-1: Identities and credentials are managed for authorized devices and users.",
                "CIS Control 4.1: Maintain secure configurations for enterprise assets.",
            ],
            metadatas=[
                {
                    "framework": "ISO27001",
                    "control_id": "A.9.1.1",
                    "source_file": "sample_seed",
                    "page": 0,
                },
                {
                    "framework": "NIST",
                    "control_id": "PR.AC-1",
                    "source_file": "sample_seed",
                    "page": 0,
                },
                {
                    "framework": "CIS",
                    "control_id": "Control 4.1",
                    "source_file": "sample_seed",
                    "page": 0,
                },
            ],
            ids=["seed_iso_27001_a_9_1_1", "seed_nist_pr_ac_1", "seed_cis_4_1"],
        )

        logger.info("Sample compliance data initialized.")

    def secure_query(
        self,
        user_token: str,
        finding: TechnicalFindingInput,
        *,
        n_results: int = 3,
    ) -> dict[str, Any]:
        """Secure query method returning dict response."""

        matches = self.secure_query_v2(
            user_token=user_token,
            finding=finding,
            n_results=n_results,
        )

        return {
            "status": "Success",
            "count": len(matches),
            "matches": [match.model_dump() for match in matches],
        }

    def secure_query_v2(
        self,
        user_token: str,
        finding: TechnicalFindingInput,
        *,
        n_results: int = 3,
    ) -> list[ComplianceMatchSchema]:
        """Return closest matching compliance controls."""

        if not verify_access(user_token, self._shared_secret):
            logger.warning("Blocked unauthorized database query attempt.")
            raise PermissionError("Access denied: invalid or missing security token.")

        if not isinstance(n_results, int) or isinstance(n_results, bool):
            raise TypeError("n_results must be an integer.")

        if not 1 <= n_results <= MAX_RESULTS_LIMIT:
            raise ValueError(f"n_results must be between 1 and {MAX_RESULTS_LIMIT}.")

        available_records = self.collection.count()

        if available_records == 0:
            logger.info("Compliance database is empty.")
            return []

        query_text = build_query_text(finding)

        try:
            result = self.collection.query(
                query_texts=[query_text],
                n_results=min(n_results, available_records),
                include=["documents", "metadatas", "distances"],
            )
        except Exception:
            logger.exception("ChromaDB query failed.")
            raise RuntimeError("Compliance query failed.")

        documents = (result.get("documents") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]

        matches: list[ComplianceMatchSchema] = []

        for document, metadata, distance in zip(documents, metadatas, distances):
            metadata_dict = metadata if isinstance(metadata, dict) else {}

            framework = safe_metadata_value(
                metadata_dict,
                "framework",
                default="UNKNOWN",
            )

            control_id = safe_metadata_value(
                metadata_dict,
                "control_id",
                "id",
                default="N/A",
            )

            source_file = metadata_dict.get("source_file")
            page = metadata_dict.get("page")

            try:
                page_value = int(page) if page is not None else None
            except (TypeError, ValueError):
                page_value = None

            matches.append(
                ComplianceMatchSchema(
                    matched_rule=str(document),
                    framework=framework,
                    control_id=control_id,
                    source_file=str(source_file) if source_file else None,
                    page=page_value,
                    distance=float(distance) if distance is not None else None,
                )
            )

        logger.info("Compliance query completed. Matches returned: %s", len(matches))

        return matches


# ==========================================
# LOCAL TEST RUNNER
# ==========================================

def main() -> None:
    """Run small local smoke test."""

    db = SecureComplianceDatabase()
    token = load_shared_secret()

    test_finding = TechnicalFindingInput(
        vulnerability_title="Weak Password Policy",
        description="Passwords are shorter than eight characters and access control is weak.",
        severity="Medium",
        cve=None,
    )

    response = db.secure_query(
        user_token=token,
        finding=test_finding,
        n_results=3,
    )

    print("\n--- RiskLens Secure Query Result ---")
    print(f"Status: {response['status']}")
    print(f"Matches: {response['count']}")

    for index, match in enumerate(response["matches"], start=1):
        print(f"\nMatch {index}")
        print(f"Framework : {match['framework']}")
        print(f"Control   : {match['control_id']}")
        print(f"Source    : {match['source_file']}")
        print(f"Page      : {match['page']}")
        print(f"Distance  : {match['distance']}")
        print(f"Rule      : {match['matched_rule'][:500]}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Error: {error}")