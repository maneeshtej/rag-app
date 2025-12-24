from langchain_ollama import ChatOllama

def create_llm(
    model: str = "phi3:mini",
    temperature: float = 0.2,
):
    return ChatOllama(
        model=model,
        temperature=temperature,
        num_predict=1024,
    )

def create_vision_llm(model:str = "llava:7b", temperature:float = 0.2):
    return ChatOllama(model=model, temperature=temperature)