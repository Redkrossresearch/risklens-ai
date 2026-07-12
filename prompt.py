PROMPT_TEMPLATE = """
You are an Expert Cyber Security Risk Analyst.
Analyze the following vulnerability.
Title: {title}
Severity: {severity}
Description: {description}
Return ONLY valid JSON.
Return exactly this structure:
{{
    "risk_title":"",
    "executive_summary":"",
    "business_impact":"",
    "likelihood":"",
    "risk_rating":"",
    "risk_score":0,
    "remediation":"",
    "compliance":
    {{
        "iso27001":"",
        "nist":"",
        "cis":""
    }},
    "ticket":
    {{
        "ticket_id":"",
        "status":"",
        "assigned_to":"",
        "due_date":"",
        "priority":""
    }}
}}
"""