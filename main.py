from fastapi import FastAPI
from models import VulnerabilityModel

app = FastAPI(title="RiskLens AI")

@app.get("/")
def root():
    return {"message": "RiskLens AI is running"}