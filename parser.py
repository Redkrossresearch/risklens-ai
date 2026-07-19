import pandas as pd
from models import VulnerabilityModel
import uuid

def parse_csv(file_path: str):
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='utf-16')
    df.columns = df.columns.str.strip().str.lower()
    vulnerabilities = []
    for _, row in df.iterrows():
        vuln = VulnerabilityModel(
            vulnerability_id=str(uuid.uuid4()),
            title=str(row.get('title', row.get('name', 'Unknown'))).strip(),
            cve=str(row.get('cve', 'N/A')).strip(),
            severity=str(row.get('severity', 'Unknown')).strip(),
            host=str(row.get('host', 'Unknown')).strip(),
            description=str(row.get('description', 'N/A')).strip(),
        )
        vulnerabilities.append(vuln.model_dump())
    return vulnerabilities

def parse_xlsx(file_path: str):
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip().str.lower()
    vulnerabilities = []
    for _, row in df.iterrows():
        vuln = VulnerabilityModel(
            vulnerability_id=str(uuid.uuid4()),
            title=str(row.get('title', 'Unknown')).strip(),
            cve=str(row.get('cve', 'N/A')).strip(),
            severity=str(row.get('severity', 'Unknown')).strip(),
            host=str(row.get('host', 'Unknown')).strip(),
            description=str(row.get('description', 'N/A')).strip(),
        )
        vulnerabilities.append(vuln.model_dump())
    return vulnerabilities