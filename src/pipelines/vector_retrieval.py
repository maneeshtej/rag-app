from database.vector_retriever import VectorRetriever
from src.models.user import User

class VectorRetrieval:
    def __init__(self, retriever:VectorRetriever=None, vectorstore=None):
        self.retriever = retriever
        self.vectorstore = vectorstore

    def set_retriever(self, retriever):
        self.retriever = retriever

    def set_vectorstore(self, vectorstore):
        self.vectorstore = vectorstore

    def run(self, query: str, user: User):
        # print("Embedding fn:", self.retriever.vectorstore.embedding_function)

        if not all ([self.retriever]):
            raise ValueError("Items not passed...")

        return self.retriever.retrieve(
            query=query,
            user=user,
            k=5
        )
    
    def list_files(self, user:User):
        return self.retriever.list_files(user)
    
    def delete_file(self, source:str):
        return self.retriever.delete_file(source)
    