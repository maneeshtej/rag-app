from pydoc import doc
from typing import List
from langchain_core.documents import Document
from src.models.user import User
from src.schema import realisation_rules


class MainPipeline:
    def __init__(
        self,
        vector_ingestion,
        retrieval,
        answer,
        guidance_ingestor,
        scrape_ingestion

    ):
        self.vector_ingestion = vector_ingestion
        self.retrieval = retrieval
        self.answer = answer
        self.guidance_ingestor = guidance_ingestor
        self.scrape_ingestion = scrape_ingestion

    # ---------- INGESTION ----------

    def ingest_vector(self, loader, user: User):
        if not self.vector_ingestion:
            raise ValueError("Vector scrape_ingestion is not configured")

        return self.vector_ingestion.run(loader, user)

    def ingest_sql(self, path: str, user: User):
        if not self.sql_ingestion:
            raise ValueError("SQL scrape_ingestion is not configured")

        return self.sql_ingestion.run(path, user)
    
    def ingest_schema(
        self,
        *,
        realisation_rules: list[dict],
        schema: list[dict],
        generate_rules: list[dict],
        truncate:bool = False
    ) -> dict:
        
        if truncate:
            self.guidance_ingestor.truncate()

        rule_items = self.guidance_ingestor.ingest(
            rules=realisation_rules
        )

        schema_items = self.guidance_ingestor.ingest(
            rules=schema
        )

        generate_items = self.guidance_ingestor.ingest(
            rules=generate_rules
        )

        return {
            "rules": rule_items,
            "schema": schema_items,
            "generate": generate_items
        }

    
    def ingest_faculty_profiles(self, *, profiles:list[dict], dept_name:str, user:User, truncate: bool = False):
        if truncate:
            self.scrape_ingestion.truncate_tables(tables=["faculty", "faculty_subjects", "subjects"])
        return self.scrape_ingestion.ingest_faculty_profiles(profiles=profiles, dept_name=dept_name, user=user)

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

