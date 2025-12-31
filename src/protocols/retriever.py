from typing import Protocol
from src.models.user import User

class Retriever(Protocol):
    def retrieve(self, *, query:str, user:User, limit:int) -> list:
        pass