from langchain_community.llms import Ollama
from models import VulnerabilityModel
from prompt import PROMPT_TEMPLATE

llm = Ollama(model="qwen3:1.7b")

print("========== RiskLens AI ==========\n")

vulnerability = VulnerabilityModel(
    vulnerability_id=input("Vulnerability ID: "),
    title=input("Title: "),
    cve=input("CVE: "),
    severity=input("Severity: "),
    host=input("Host: "),
    description=input("Description: ")
)

prompt = PROMPT_TEMPLATE.format(
    title=vulnerability.title,
    severity=vulnerability.severity,
    description=vulnerability.description
)

print("\nGenerating AI Risk Analysis...\n")

response = llm.invoke(prompt)

print("========== AI RISK ANALYSIS ==========\n")
print(response)

print("\n========== Vulnerability Details ==========\n")
print(vulnerability.model_dump_json(indent=4))