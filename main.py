from fastapi import FastAPI, Depends, HTTPException
from fastapi import Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import Base, engine, get_db
from db_models import User, Vulnerability
from auth import hash_password, verify_password, create_access_token
from upload import router as upload_router, parsed_vulnerabilities as upload_vulnerabilities
from fastapi.staticfiles import StaticFiles
from ticketing.routes import router as ticketing_router
from ticketing.models import Ticket
from report_generator import generate_executive_report, generate_technical_report
from auth import get_role_from_token
from fastapi.responses import FileResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title="RiskLens AI")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(upload_router)
app.include_router(ticketing_router)

class UserRegister(BaseModel):
    username: str
    password: str
    role: str = "viewer"

class UserLogin(BaseModel):
    username: str
    password: str

uploaded_files_log = []

COMPLIANCE_DATA = {
    "ISO 27001": 81,
    "NIST CSF": 76,
    "GDPR": 63,
    "PCI-DSS": 58,
    "CIS v8": 79,
    "HIPAA": 44
}

@app.get("/")
def root():
    return {"message": "RiskLens AI is running"}

@app.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    if user.role not in ["admin", "analyst", "viewer"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    new_user = User(
        username=user.username,
        password=hash_password(user.password),
        role=user.role
    )
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully", "role": user.role}

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    token = create_access_token({
        "sub": db_user.username,
        "role": db_user.role
    })
    return {"access_token": token, "token_type": "bearer", "role": db_user.role}

@app.get("/admin/users")
def get_users(token: str, db: Session = Depends(get_db)):
    role = get_role_from_token(token)
    if role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    users = db.query(User).all()
    return {"users": [u.username for u in users]}

@app.get("/analyst/vulnerabilities")
def get_vulnerabilities(token: str):
    role = get_role_from_token(token)
    if role not in ["admin", "analyst"]:
        raise HTTPException(status_code=403, detail="Access denied")
    return {"vulnerabilities": upload_vulnerabilities}

@app.get("/api/stats")
def get_stats():
    total = len(upload_vulnerabilities)
    critical = sum(1 for v in upload_vulnerabilities if v.get("severity","").lower() == "critical")
    high = sum(1 for v in upload_vulnerabilities if v.get("severity","").lower() == "high")
    medium = sum(1 for v in upload_vulnerabilities if v.get("severity","").lower() == "medium")
    low = sum(1 for v in upload_vulnerabilities if v.get("severity","").lower() == "low")
    return {
        "total_vulnerabilities": total,
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low,
        "compliance": COMPLIANCE_DATA,
    }

@app.post("/analyze")
def analyze(token: str, vulnerability_id: str, title: str, severity: str, description: str):
    role = get_role_from_token(token)
    if role not in ["admin", "analyst"]:
        raise HTTPException(status_code=403, detail="Access denied")
    from ai_analyzer import analyze_vulnerability
    result = analyze_vulnerability(title, severity, description)
    return {
        "vulnerability_id": vulnerability_id,
        "title": title,
        "severity": severity,
        "ai_analysis": result["ai_analysis"],
        "status": result["status"]
    }

@app.get("/report/executive")
def executive_report():
    path = generate_executive_report(upload_vulnerabilities, COMPLIANCE_DATA)
    return {"message": "Executive report generated", "path": path}

@app.get("/report/technical")
def technical_report():
    path = generate_technical_report(upload_vulnerabilities, COMPLIANCE_DATA)
    return {"message": "Technical report generated", "path": path}
@app.get("/report/executive/download")
def download_executive_report():
    path = generate_executive_report(upload_vulnerabilities, COMPLIANCE_DATA)
    return FileResponse(path, media_type="application/pdf", filename="executive_report.pdf")

@app.get("/report/technical/download")
def download_technical_report():
    path = generate_technical_report(upload_vulnerabilities, COMPLIANCE_DATA)
    return FileResponse(path, media_type="application/pdf", filename="technical_report.pdf")