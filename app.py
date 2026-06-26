from langchain_community.llms import Ollama

llm = Ollama(model="qwen3:1.7b")

prompt = """
You are a Cyber Security Risk Analyst.

Analyze the following vulnerability.

Title: SMB Signing Disabled
Severity: Critical
Description:
SMB signing is disabled on the server.

Provide:
1. Risk Title
2. Business Impact
3. Likelihood
4. Risk Rating
5. Remediation
"""

response = llm.invoke(prompt)

print(response)