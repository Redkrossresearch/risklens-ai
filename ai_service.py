from langchain_community.llms import Ollama
import re

from prompt import PROMPT_TEMPLATE

llm = Ollama(model="qwen3:1.7b")


def extract_risk_score(text):

    score = re.search(r'(\d{1,3})\s*/\s*100', text)

    if score:
        return int(score.group(1))

    score = re.search(r'Risk Score.*?(\d{1,3})', text, re.IGNORECASE)

    if score:
        return int(score.group(1))

    return None


def generate_risk_analysis(vulnerability):

    prompt = PROMPT_TEMPLATE.format(
        title=vulnerability.title,
        severity=vulnerability.severity,
        description=vulnerability.description
    )

    response = llm.invoke(prompt)

    vulnerability.risk_score = extract_risk_score(response)

    return response