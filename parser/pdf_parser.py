import pdfplumber
import re
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import VulnerabilityModel
from parser.validator import validate_severity, validate_cve
from parser.logger_config import logger


def parse_pdf(file_path):

    try:
        text = ""

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"

        logger.info("PDF file loaded successfully.")
        

    except FileNotFoundError:
        print("PDF file not found.")
        return []

    except Exception as e:
        print(e)
        return []

    vulnerabilities = []

    pattern = re.findall(
    r"Title:\s*(.*?)\s*"
    r"CVE:\s*(.*?)\s*"
    r"Severity:\s*(.*?)\s*"
    r"Host:\s*(.*?)\s*"
    r"Description:\s*(.*?)(?=Title:|$)",
    text,
    re.DOTALL
    )

    seen_cves = set()

    for index, item in enumerate(pattern):

        title, cve, severity, host, description = item

        title = title.strip()
        cve = cve.strip()
        severity = severity.strip()
        host = host.strip()
        description = description.strip()

        if not validate_severity(severity):
            continue

        if not validate_cve(cve):
            continue

        if cve in seen_cves:
            continue

        seen_cves.add(cve)

        vulnerability = VulnerabilityModel(
            vulnerability_id=f"VULN-{index+1:03}",
            title=title,
            cve=cve,
            severity=severity,
            host=host,
            description=description
        )

        vulnerabilities.append(vulnerability)

    print("\n========== PDF Parsing Summary ==========")
    print(f"Valid Records : {len(vulnerabilities)}")

    return vulnerabilities


if __name__ == "__main__":

    file_name = input("Enter PDF file name: ")

    vulnerabilities = parse_pdf(f"samples/{file_name}")

    for vulnerability in vulnerabilities:
        print(vulnerability.model_dump())