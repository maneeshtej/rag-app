from pydoc import doc
from typing import List
from langchain_core.documents import Document
from src.models.user import User


class MainPipeline:
    def __init__(
        self,
        vector_ingestion,
        sql_ingestion,
        retrieval,
        answer,
        guidance_ingestor
    ):
        self.vector_ingestion = vector_ingestion
        self.sql_ingestion = sql_ingestion
        self.retrieval = retrieval
        self.answer = answer
        self.guidance_ingestor = guidance_ingestor

    # ---------- INGESTION ----------

    def ingest_vector(self, loader, user: User):
        if not self.vector_ingestion:
            raise ValueError("Vector ingestion is not configured")

        return self.vector_ingestion.run(loader, user)

    def ingest_sql(self, path: str, user: User):
        if not self.sql_ingestion:
            raise ValueError("SQL ingestion is not configured")

        return self.sql_ingestion.run(path, user)

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

        if not all([self.retrieval, self.answer]):
            raise ValueError("Inference pipeline is not fully configured")

        docs = self.retrieval.run(query, user)

        if test:
            return docs
        
        vector_docs = docs.get("vector")
        sql_rows = docs.get("sql")

        return self.answer.run(query, vector_docs=vector_docs, sql_rows=sql_rows, chat_history=chat_history)
    
    def ingest_schema(self, *, rules:list[dict], schema:list[dict], truncate:bool=False) -> dict:
        
        rules_output = self.guidance_ingestor.ingest_hints(rows=rules, truncate=truncate)
        schema_output = self.guidance_ingestor.ingest_schema(rows=schema, truncate=truncate)

        return {
            "rules": rules_output,
            "schema": schema_output
        }
