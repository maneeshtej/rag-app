from src.models.user import User


class VectorRetrieval:
    def __init__(self, vector_retriever):
        self.vector_retriever = vector_retriever

    def __enhance_query(self, *, query:str):
        raise NotImplementedError
    
    def __reranking(self, *, chunks:list[dict]):
        raise NotImplementedError

    def retriever(self, *, query:str, user:User, k:int=5):
        raise NotImplementedError