PROMPT_TEMPLATE = """
You are a Cyber Security Risk Analyst.

Analyze the following vulnerability.

Title: {title}
Severity: {severity}
Description: {description}

Generate the following:

1. Risk Title
2. Business Impact
3. Likelihood
4. Risk Rating
5. Remediation

Return the response in a clear and professional format.
"""