from parser import parse_csv, parse_xlsx
import os
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from pypdf import PdfReader
from ai_service import generate_risk_analysis
from models import VulnerabilityModel
from database import get_db
from db_models import Vulnerability
from auth import get_current_user

router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

parsed_vulnerabilities = []
uploaded_files_log = []

@router.post("/upload/csv")
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    vulnerabilities = parse_csv(file_path)

    analyzed_vulnerabilities = []
    for vuln in vulnerabilities:
        vuln_model = VulnerabilityModel(**vuln)
        ai_result = generate_risk_analysis(vuln_model)
        analyzed_vulnerabilities.append(ai_result)

        # Check if this vulnerability (same CVE + host) already exists.
        # If it does, update that row instead of creating a duplicate.
        existing = None
        if ai_result.get("cve") and ai_result.get("host"):
            existing = (
                db.query(Vulnerability)
                .filter(
                    Vulnerability.cve == ai_result.get("cve"),
                    Vulnerability.host == ai_result.get("host"),
                )
                .first()
            )

        if existing:
            existing.title = ai_result.get("title")
            existing.severity = ai_result.get("severity")
            existing.description = ai_result.get("description")
            existing.risk_title = ai_result.get("risk_title")
            existing.executive_summary = ai_result.get("executive_summary")
            existing.business_impact = ai_result.get("business_impact")
            existing.likelihood = ai_result.get("likelihood")
            existing.risk_rating = ai_result.get("risk_rating")
            existing.risk_score = ai_result.get("risk_score")
            existing.remediation = ai_result.get("remediation")
            existing.compliance = ai_result.get("compliance")
            existing.ticket = ai_result.get("ticket")
            # Keep the original vulnerability_id/row — just refresh the data
            ai_result["vulnerability_id"] = existing.vulnerability_id
            ai_result["duplicate_updated"] = True
        else:
            db_vuln = Vulnerability(
                vulnerability_id=ai_result.get("vulnerability_id"),
                title=ai_result.get("title"),
                cve=ai_result.get("cve"),
                severity=ai_result.get("severity"),
                host=ai_result.get("host"),
                description=ai_result.get("description"),
                risk_title=ai_result.get("risk_title"),
                executive_summary=ai_result.get("executive_summary"),
                business_impact=ai_result.get("business_impact"),
                likelihood=ai_result.get("likelihood"),
                risk_rating=ai_result.get("risk_rating"),
                risk_score=ai_result.get("risk_score"),
                remediation=ai_result.get("remediation"),
                compliance=ai_result.get("compliance"),
                ticket=ai_result.get("ticket"),
            )
            db.add(db_vuln)
            ai_result["duplicate_updated"] = False

    db.commit()

    parsed_vulnerabilities.extend(analyzed_vulnerabilities)
    uploaded_files_log.append({"name": file.filename, "type": "CSV", "status": "Parsed"})

    return {
        "message": "CSV uploaded and AI analyzed",
        "total": len(analyzed_vulnerabilities),
        "data": analyzed_vulnerabilities
    }

@router.post("/upload/xlsx")
async def upload_xlsx(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only XLSX files allowed")
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    df = pd.read_excel(file_path)
    uploaded_files_log.append({"name": file.filename, "type": "XLSX", "status": "Parsed"})
    return {"message": "XLSX uploaded", "rows": len(df), "columns": list(df.columns)}

@router.post("/upload/pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    reader = PdfReader(file_path)
    pages = len(reader.pages)
    uploaded_files_log.append({"name": file.filename, "type": "PDF", "status": "Uploaded"})
    return {"message": "PDF uploaded", "pages": pages}