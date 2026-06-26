import os
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException
from pypdf import PdfReader

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload/csv")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    df = pd.read_csv(file_path)
    return {"message": "CSV uploaded", "rows": len(df), "columns": list(df.columns)}

@router.post("/upload/xlsx")
async def upload_xlsx(file: UploadFile = File(...)):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only XLSX files allowed")
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    df = pd.read_excel(file_path)
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
    return {"message": "PDF uploaded", "pages": pages}