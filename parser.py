import pandas as pd
import pdfplumber
from models import VulnerabilityModel
import uuid

QUALYS_SEVERITY_MAP = {
    "5": "Critical",
    "4": "High",
    "3": "Medium",
    "2": "Low",
    "1": "Low",
}

def normalize_severity(value: str) -> str:
    value = value.strip()
    if value in QUALYS_SEVERITY_MAP:
        return QUALYS_SEVERITY_MAP[value]
    return value if value else "Unknown"

def parse_csv(file_path: str):
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='utf-16')
    df.columns = df.columns.str.strip().str.lower()
    vulnerabilities = []
    for _, row in df.iterrows():
        raw_severity = str(row.get('severity', row.get('risk', row.get('risk factor', 'Unknown')))).strip()
        vuln = VulnerabilityModel(
            vulnerability_id=str(uuid.uuid4()),
            title=str(row.get('title', row.get('name', row.get('plugin name', 'Unknown')))).strip(),
            cve=str(row.get('cve', row.get('cves', row.get('cve id', 'N/A')))).strip(),
            severity=normalize_severity(raw_severity),
            host=str(row.get('host', row.get('ip address', row.get('asset', row.get('ip', 'Unknown'))))).strip(),
            description=str(row.get('description', row.get('synopsis', row.get('threat', 'N/A')))).strip(),
        )
        vulnerabilities.append(vuln.model_dump())
    return vulnerabilities

def parse_xlsx(file_path: str):
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip().str.lower()
    vulnerabilities = []
    for _, row in df.iterrows():
        raw_severity = str(row.get('severity', row.get('risk', row.get('risk factor', 'Unknown')))).strip()
        vuln = VulnerabilityModel(
            vulnerability_id=str(uuid.uuid4()),
            title=str(row.get('title', row.get('name', row.get('plugin name', 'Unknown')))).strip(),
            cve=str(row.get('cve', row.get('cves', row.get('cve id', 'N/A')))).strip(),
            severity=normalize_severity(raw_severity),
            host=str(row.get('host', row.get('ip address', row.get('asset', row.get('ip', 'Unknown'))))).strip(),
            description=str(row.get('description', row.get('synopsis', row.get('threat', 'N/A')))).strip(),
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
                    raw_severity = str(row_dict.get('severity', row_dict.get('risk', 'Unknown')) or 'Unknown').strip()
                    vuln = VulnerabilityModel(
                        vulnerability_id=str(uuid.uuid4()),
                        title=str(row_dict.get('title', row_dict.get('name', 'Unknown')) or 'Unknown').strip(),
                        cve=str(row_dict.get('cve', row_dict.get('cve id', 'N/A')) or 'N/A').strip(),
                        severity=normalize_severity(raw_severity),
                        host=str(row_dict.get('host', row_dict.get('ip', 'Unknown')) or 'Unknown').strip(),
                        description=str(row_dict.get('description', row_dict.get('synopsis', 'N/A')) or 'N/A').strip(),
                    )
                    vulnerabilities.append(vuln.model_dump())
    return vulnerabilities