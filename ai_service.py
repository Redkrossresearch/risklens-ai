from langchain_community.llms import Ollama
from prompt import PROMPT_TEMPLATE
from models import ComplianceModel, TicketModel
import json
import random

# NOTE: temperature=0.1 added — lower randomness so output format is consistent.
# NOTE: If output is still inconsistent, the model (qwen3:1.7b) is likely too small
# for this task. Check if qwen3:14b runs on this machine (see project plan Week 1 risk).
llm = Ollama(model="qwen3:1.7b", temperature=0.1)


VALID_RATINGS = ["Critical", "High", "Medium", "Low"]


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


def clean_json_response(response):
    """
    Small/local LLMs often wrap JSON in markdown fences or add stray text
    before/after the JSON object. This strips that so json.loads doesn't fail
    and doesn't silently parse garbage.
    """

    response = response.strip()

    # Remove markdown code fences if present
    if response.startswith("```"):
        parts = response.split("```")
        if len(parts) >= 2:
            response = parts[1]
            if response.strip().lower().startswith("json"):
                response = response.strip()[4:]

    response = response.strip()

    # If there's stray text before/after the JSON object, extract the
    # outermost {...} block instead of trusting the whole string.
    start = response.find("{")
    end = response.rfind("}")
    if start != -1 and end != -1 and end > start:
        response = response[start:end + 1]

    return response.strip()


def validate_rating(value, fallback="Not Rated"):
    """
    risk_rating and likelihood must be one of the fixed categories.
    The model sometimes returns the right word wrapped in extra text
    ("Critical: due to...", "Critical - exposed port", "high risk here"),
    and for risk_rating specifically it sometimes returns a 1-10 numeric
    scale instead of a word (e.g. "9", "10") despite the prompt asking
    for an enum. We handle both cases before falling back.
    """

    if value is None:
        return fallback

    # Handle numeric ratings (model sometimes uses a 1-10 scale)
    if isinstance(value, (int, float)):
        return _map_numeric_rating(value)

    if not isinstance(value, str) or not value.strip():
        return fallback

    cleaned = value.strip()

    # If the whole string is just a number, map it
    if cleaned.replace(".", "", 1).isdigit():
        return _map_numeric_rating(float(cleaned))

    # Try exact match first (after stripping common separators)
    for sep in [":", "-", ",", ";"]:
        head = cleaned.split(sep)[0].strip().title()
        if head in VALID_RATINGS:
            return head

    # Fall back to checking if a valid word appears as the first word
    first_word = cleaned.split()[0].strip().title() if cleaned.split() else ""
    if first_word in VALID_RATINGS:
        return first_word

    # Last resort: check if any valid rating word appears anywhere in the text
    lowered = cleaned.lower()
    for rating in VALID_RATINGS:
        if rating.lower() in lowered:
            return rating

    return fallback


def _map_numeric_rating(num):
    """
    Maps a 1-10 (or 0-100) style numeric rating to a category.
    Assumes 1-10 scale since that's what the model has been returning.
    """
    if num > 10:
        # Looks like a 0-100 score instead of 1-10
        if num >= 90:
            return "Critical"
        elif num >= 70:
            return "High"
        elif num >= 40:
            return "Medium"
        else:
            return "Low"

    if num >= 9:
        return "Critical"
    elif num >= 7:
        return "High"
    elif num >= 4:
        return "Medium"
    else:
        return "Low"


def validate_compliance_field(value, fallback="Not mapped"):
    """
    Compliance fields must be a real control code / description, not empty,
    not a bare number, not "Yes"/"No". If it doesn't look like a real
    mapping, fall back instead of storing meaningless data.
    """

    if not isinstance(value, str):
        return fallback

    cleaned = value.strip()

    if not cleaned:
        return fallback

    if cleaned.isdigit():
        return fallback

    if cleaned.lower() in ["yes", "no", "n/a", "na"]:
        return fallback

    return cleaned


def generate_risk_analysis(vulnerability):

    prompt = PROMPT_TEMPLATE.format(
        title=vulnerability.title,
        severity=vulnerability.severity,
        description=vulnerability.description
    )

    response = llm.invoke(prompt)
    cleaned_response = clean_json_response(response)

    try:

        data = json.loads(cleaned_response)

        # AI Fields
        vulnerability.risk_title = data.get("risk_title")
        vulnerability.executive_summary = data.get("executive_summary")
        vulnerability.business_impact = data.get("business_impact")

        vulnerability.likelihood = validate_rating(
            data.get("likelihood"), fallback="Not Rated"
        )
        vulnerability.risk_rating = validate_rating(
            data.get("risk_rating"), fallback="Not Rated"
        )

        # Risk Score
        vulnerability.risk_score = calculate_risk_score(
            vulnerability.severity,
            data.get("risk_score")
        )

        vulnerability.remediation = data.get("remediation")

        # Compliance
        compliance_data = data.get("compliance") or {}

        vulnerability.compliance = ComplianceModel(
            iso27001=validate_compliance_field(compliance_data.get("iso27001")),
            nist=validate_compliance_field(compliance_data.get("nist")),
            cis=validate_compliance_field(compliance_data.get("cis"))
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