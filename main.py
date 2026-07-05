from fastapi import FastAPI, Depends, HTTPException
from fastapi import Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from auth import hash_password, verify_password, create_access_token
from upload import router as upload_router
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="RiskLens AI")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(upload_router)

class UserRegister(BaseModel):
    username: str
    password: str
    role: str = "viewer"  # default viewer

class UserLogin(BaseModel):
    username: str
    password: str

users_db = {}  # { username: { "password": hashed, "role": role } }

@app.get("/")
def root():
    return {"message": "RiskLens AI is running"}

@app.post("/register")
def register(user: UserRegister):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    if user.role not in ["admin", "analyst", "viewer"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    users_db[user.username] = {
        "password": hash_password(user.password),
        "role": user.role
    }
    return {"message": "User registered successfully", "role": user.role}

@app.post("/login")
def login(user: UserLogin):
    if user.username not in users_db:
        raise HTTPException(status_code=400, detail="User not found")
    if not verify_password(user.password, users_db[user.username]["password"]):
        raise HTTPException(status_code=400, detail="Incorrect password")
    token = create_access_token({
        "sub": user.username,
        "role": users_db[user.username]["role"]
    })
    return {"access_token": token, "token_type": "bearer", "role": users_db[user.username]["role"]}

from auth import get_role_from_token
parsed_vulnerabilities = []
uploaded_files_log = []

@app.get("/admin/users")
def get_users(token: str):
    role = get_role_from_token(token)
    if role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return {"users": list(users_db.keys())}

@app.get("/analyst/vulnerabilities")  
def get_vulnerabilities(token: str):
    role = get_role_from_token(token)
    if role not in ["admin", "analyst"]:
        raise HTTPException(status_code=403, detail="Access denied")
    return {"message": "Vulnerabilities accessible"}
from report_generator import generate_executive_report, generate_technical_report

# Sample compliance data
COMPLIANCE_DATA = {
    "ISO 27001": 81,
    "NIST CSF": 76,
    "GDPR": 63,
    "PCI-DSS": 58,
    "CIS v8": 79,
    "HIPAA": 44
}

@app.get("/report/executive")
def executive_report():
    path = generate_executive_report(parsed_vulnerabilities, COMPLIANCE_DATA)
    return {"message": "Executive report generated", "path": path}

@app.get("/report/technical")
def technical_report():
    path = generate_technical_report(parsed_vulnerabilities, COMPLIANCE_DATA)
    return {"message": "Technical report generated", "path": path}
from ai_analyzer import analyze_vulnerability

@app.post("/analyze")
def analyze(token: str, vulnerability_id: str, title: str, severity: str, description: str):
    role = get_role_from_token(token)
    if role not in ["admin", "analyst"]:
        raise HTTPException(status_code=403, detail="Access denied")
    result = analyze_vulnerability(title, severity, description)
    return {
        "vulnerability_id": vulnerability_id,
        "title": title,
        "severity": severity,
        "ai_analysis": result["ai_analysis"],
        "status": result["status"]
    }
@app.get("/api/stats")
def get_stats():
    total = len(parsed_vulnerabilities)
    critical = sum(1 for v in parsed_vulnerabilities if v.get("severity","").lower() == "critical")
    high = sum(1 for v in parsed_vulnerabilities if v.get("severity","").lower() == "high")
    medium = sum(1 for v in parsed_vulnerabilities if v.get("severity","").lower() == "medium")
    low = sum(1 for v in parsed_vulnerabilities if v.get("severity","").lower() == "low")
    return {
        "total_vulnerabilities": total,
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low,
        "files_processed": len(uploaded_files_log) if 'uploaded_files_log' in globals() else 0,
        "uploaded_files": uploaded_files_log[-4:] if 'uploaded_files_log' in globals() else [],
        "compliance": {
            "ISO 27001": 81,
            "NIST CSF": 76,
            "GDPR": 63,
            "PCI-DSS": 58,
            "CIS v8": 79,
            "HIPAA": 44
        },
        "tickets": [
            {"id": "#001", "text": "Fix CVE-2024-1234 on prod server", "severity": "Critical"},
            {"id": "#002", "text": "GDPR data retention policy gap", "severity": "High"},
            {"id": "#003", "text": "SSL cert renewal — 14 days left", "severity": "Medium"},
            {"id": "#004", "text": "API rate limiting not configured", "severity": "Low"},
        ]
    }