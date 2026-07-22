import pandas as pd
import pdfplumber
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

def parse_pdf(file_path: str):
    vulnerabilities = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if not table or len(table) < 2:
                    continue
                headers = [str(h).strip().lower() if h else "" for h in table[0]]
                for row_data in table[1:]:
                    row_dict = dict(zip(headers, row_data))
                    vuln = VulnerabilityModel(
                        vulnerability_id=str(uuid.uuid4()),
                        title=str(row_dict.get('title', 'Unknown') or 'Unknown').strip(),
                        cve=str(row_dict.get('cve', 'N/A') or 'N/A').strip(),
                        severity=str(row_dict.get('severity', 'Unknown') or 'Unknown').strip(),
                        host=str(row_dict.get('host', 'Unknown') or 'Unknown').strip(),
                        description=str(row_dict.get('description', 'N/A') or 'N/A').strip(),
                    )
                    vulnerabilities.append(vuln.model_dump())
    return vulnerabilities