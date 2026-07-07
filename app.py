from models import VulnerabilityModel
from ai_service import generate_risk_analysis
import json

print("========== RiskLens AI ==========\n")

vulnerability = VulnerabilityModel(
    vulnerability_id=input("Vulnerability ID: "),
    title=input("Title: "),
    cve=input("CVE: "),
    severity=input("Severity: "),
    host=input("Host: "),
    description=input("Description: ")
)

print("\nGenerating AI Risk Analysis...\n")

result = generate_risk_analysis(vulnerability)

print("\n========== AI JSON RESPONSE ==========\n")
print(json.dumps(result, indent=4))

print("\n========== UPDATED MODEL ==========\n")
print(vulnerability.model_dump_json(indent=4))