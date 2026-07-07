PROMPT_TEMPLATE = """
You are an Expert Cyber Security Risk Analyst.

Analyze the following vulnerability.

Title: {title}
Severity: {severity}
Description: {description}

Return ONLY valid JSON.

Do not write explanations.
Do not write markdown.
Do not use ```json.

Return exactly this format:

{{
    "risk_title": "",
    "executive_summary": "",
    "business_impact": "",
    "likelihood": "",
    "risk_rating": "",
    "risk_score": 0,
    "remediation": ""
}}
"""