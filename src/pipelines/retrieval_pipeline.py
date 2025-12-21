from database.pg_retrieval import PGRetriever
from models.user import User

class RetrievalPipeline:
    def __init__(self, retriever:PGRetriever=None):
        self.retriever = retriever

    def set_retriever(self, retriever):
        self.retriever = retriever

    def run(self, query: str, user: User):
        # print("Embedding fn:", self.retriever.vectorstore.embedding_function)

        if not all ([self.retriever]):
            raise ValueError("Items not passed...")

        return self.retriever.retrieve(
            query=query,
            user=user,
            k=5
        )