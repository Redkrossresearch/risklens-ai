from parser import parse_csv, parse_xlsx
import os
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException
from pypdf import PdfReader
from ai_analyzer import analyze_vulnerability

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

parsed_vulnerabilities = []
uploaded_files_log = []

@router.post("/upload/csv")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    vulnerabilities = parse_csv(file_path)

    for vuln in vulnerabilities:
        ai_result = analyze_vulnerability(
            title=vuln["title"],
            severity=vuln["severity"],
            description=vuln["description"]
        )
        vuln["ai_analysis"] = ai_result["ai_analysis"]

    parsed_vulnerabilities.extend(vulnerabilities)
    uploaded_files_log.append({"name": file.filename, "type": "CSV", "status": "Parsed"})

    return {
        "message": "CSV uploaded and AI analyzed",
        "total": len(vulnerabilities),
        "data": vulnerabilities
    }

@router.post("/upload/xlsx")
async def upload_xlsx(file: UploadFile = File(...)):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only XLSX files allowed")
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    df = pd.read_excel(file_path)
    uploaded_files_log.append({"name": file.filename, "type": "XLSX", "status": "Parsed"})
    return {"message": "XLSX uploaded", "rows": len(df), "columns": list(df.columns)}

@router.post("/upload/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    reader = PdfReader(file_path)
    pages = len(reader.pages)
    uploaded_files_log.append({"name": file.filename, "type": "PDF", "status": "Uploaded"})
    return {"message": "PDF uploaded", "pages": pages}