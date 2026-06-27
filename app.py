from langchain_community.llms import Ollama
llm = Ollama(model="qwen3:1.7b")

prompt = input("Enter vulnerability details: ")

response = llm.invoke(
    f"""
    Analyze this security vulnerability:
    
    {prompt}
    
    Give:
    1. Risk Title
    2. Business Impact
    3. Likelihood
    4. Risk Rating
    5. Remediation
    """
)

print(response)