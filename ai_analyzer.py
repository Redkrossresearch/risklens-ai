from langchain_ollama import OllamaLLM
llm = OllamaLLM(model="qwen3:1.7b")
from prompt import PROMPT_TEMPLATE


def analyze_vulnerability(title: str, severity: str, description: str) -> dict:
    try:
        prompt = PROMPT_TEMPLATE.format(
            title=title,
            severity=severity,
            description=description
        )
        response = llm.invoke(prompt)
        return {
            "status": "success",
            "ai_analysis": response
        }
    except Exception as e:
        return {
            "status": "error",
            "ai_analysis": str(e)
        }