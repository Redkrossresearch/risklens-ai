import pandas as pd
from models import VulnerabilityModel
import uuid

def parse_csv(file_path: str):
    df = pd.read_csv(file_path, encoding='utf-16')
    vulnerabilities = []
    for _, row in df.iterrows():
        vuln = VulnerabilityModel(
            vulnerability_id=str(uuid.uuid4()),
            title=str(row.get("title", row.get("Name", row.get("Plugin Name", "Unknown")))),
            cve=str(row.get("cve", row.get("CVE", "N/A"))),
            severity=str(row.get("severity", row.get("Severity", "Unknown"))),
            host=str(row.get("host", row.get("Host", row.get("IP Address", "Unknown")))),
            description=str(row.get("description", row.get("Description", "N/A"))),
        )
        vulnerabilities.append(vuln.model_dump())
    return vulnerabilities

def parse_xlsx(file_path: str):
    df = pd.read_excel(file_path)
    vulnerabilities = []
    for _, row in df.iterrows():
        vuln = VulnerabilityModel(
            vulnerability_id=str(uuid.uuid4()),
            title=str(row.get("title", row.get("Name", row.get("Plugin Name", "Unknown")))),
            cve=str(row.get("cve", row.get("CVE", "N/A"))),
            severity=str(row.get("severity", row.get("Severity", "Unknown"))),
            host=str(row.get("host", row.get("Host", row.get("IP Address", "Unknown")))),
            description=str(row.get("description", row.get("Description", "N/A"))),
        )
        vulnerabilities.append(vuln.model_dump())
    return vulnerabilities