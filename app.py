from models import VulnerabilityModel
from ai_service import generate_risk_analysis

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

response = generate_risk_analysis(vulnerability)

print("========== AI RISK ANALYSIS ==========\n")
print(response)

print("\n========== Vulnerability Details ==========\n")
print(vulnerability.model_dump_json(indent=4))