from langchain_community.llms import Ollama
from prompt import PROMPT_TEMPLATE
from models import ComplianceModel, TicketModel
import json
import random

llm = Ollama(model="qwen3:1.7b")


def calculate_risk_score(severity, ai_score):
    """
    Use AI score if it is realistic (70-100).
    Otherwise generate a score based on severity.
    """

    if isinstance(ai_score, int) and 70 <= ai_score <= 100:
        return ai_score

    severity = severity.strip().lower()

    if severity == "critical":
        return random.randint(95, 100)

    elif severity == "high":
        return random.randint(80, 94)

    elif severity == "medium":
        return random.randint(60, 79)

    elif severity == "low":
        return random.randint(30, 59)

    else:
        return random.randint(20, 50)


def generate_risk_analysis(vulnerability):

    prompt = PROMPT_TEMPLATE.format(
        title=vulnerability.title,
        severity=vulnerability.severity,
        description=vulnerability.description
    )

    response = llm.invoke(prompt)

    try:

        data = json.loads(response)

        # AI Fields
        vulnerability.risk_title = data.get("risk_title")
        vulnerability.executive_summary = data.get("executive_summary")
        vulnerability.business_impact = data.get("business_impact")
        vulnerability.likelihood = data.get("likelihood")
        vulnerability.risk_rating = data.get("risk_rating")

        # Risk Score
        vulnerability.risk_score = calculate_risk_score(
            vulnerability.severity,
            data.get("risk_score")
        )

        vulnerability.remediation = data.get("remediation")

        # Compliance
        if data.get("compliance"):

            vulnerability.compliance = ComplianceModel(
                iso27001=data["compliance"].get("iso27001", ""),
                nist=data["compliance"].get("nist", ""),
                cis=data["compliance"].get("cis", "")
            )

        # Ticket
        if data.get("ticket"):

            vulnerability.ticket = TicketModel(
                ticket_id=data["ticket"].get("ticket_id", ""),
                status=data["ticket"].get("status", ""),
                assigned_to=data["ticket"].get("assigned_to", ""),
                due_date=data["ticket"].get("due_date", ""),
                priority=data["ticket"].get("priority", "")
            )

        return vulnerability.model_dump()

    except json.JSONDecodeError:

        return {
            "error": "Invalid JSON received from AI",
            "raw_response": response
        }

    except Exception as e:

        return {
            "error": str(e),
            "raw_response": response
        }