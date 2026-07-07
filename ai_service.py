from langchain_community.llms import Ollama
from prompt import PROMPT_TEMPLATE
import json

llm = Ollama(model="qwen3:1.7b")


def generate_risk_analysis(vulnerability):

    prompt = PROMPT_TEMPLATE.format(
        title=vulnerability.title,
        severity=vulnerability.severity,
        description=vulnerability.description
    )

    response = llm.invoke(prompt)

    try:

        data = json.loads(response)

        vulnerability.risk_title = data.get("risk_title")
        vulnerability.executive_summary = data.get("executive_summary")
        vulnerability.business_impact = data.get("business_impact")
        vulnerability.likelihood = data.get("likelihood")
        vulnerability.risk_rating = data.get("risk_rating")
        vulnerability.risk_score = data.get("risk_score")
        vulnerability.remediation = data.get("remediation")

        return data

    except json.JSONDecodeError:

        return {
            "error": "AI did not return valid JSON.",
            "raw_response": response
        }