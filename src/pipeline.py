from typing import List
from langchain_core.documents import Document
from src.models.user import User


class MainPipeline:
    def __init__(
        self,
        vector_ingestion,
        sql_ingestion,
        vector_retriever,
        answer,
    ):
        self.vector_ingestion = vector_ingestion
        self.sql_ingestion = sql_ingestion
        self.vector_retriever = vector_retriever
        self.answer = answer

    # ---------- INGESTION ----------

    def ingest_vector(self, loader, user: User):
        if not self.vector_ingestion:
            raise ValueError("Vector ingestion is not configured")

        return self.vector_ingestion.run(loader, user)

    def ingest_sql(self, path: str, user: User):
        if not self.sql_ingestion:
            raise ValueError("SQL ingestion is not configured")

        return self.sql_ingestion.run(path, user)

    def ingest_schema(self, docs: List[Document]):
        if not self.guidance_ingestion:
            raise ValueError("Guidance ingestion is not configured")

        return self.guidance_ingestion.ingest_schema(docs)

    # ---------- INFERENCE ----------

    def inference(
        self,
        query: str,
        user: User,
        chat_history=None,
        *,
        test: bool = False,
    ):
        chat_history = chat_history or []

        if not all([self.vector_retriever, self.answer]):
            raise ValueError("Inference pipeline is not fully configured")

        docs = self.vector_retriever.run(query, user)

        if test:
            return docs

        return self.answer.run(query, docs, chat_history)
