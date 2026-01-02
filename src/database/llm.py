from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

def create_phi_llm(
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

def create_google_llm():
    print('loaded llm')
    load_dotenv()
    return ChatGoogleGenerativeAI(model= "gemini-2.5-flash")

def create_qwen_llm():
    return ChatOllama(
    model="qwen2.5:7b-instruct",
    temperature=0.0,          
    top_p=0.9,
    repeat_penalty=1.1,
)