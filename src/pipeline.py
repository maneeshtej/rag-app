from typing import List
from src.models.user import User
from langchain_core.documents import Document

class MainPipeline:
    def __init__(self, vector_ingestion, sql_ingestion, vector_retriever, vector_store, answer, guidance_store):
        self.vector_ingestion = vector_ingestion
        self.sql_ingestion = sql_ingestion
        self.vector_retriever = vector_retriever
        self.vector_store = vector_store
        self.answer = answer
        self.guidance_store = guidance_store

    def ingest_vector(self, loader, user:User):
        if not all([self.vector_ingestion]):
            raise ValueError("Pipeline is not fully configured")
        
        return self.vector_ingestion.run(loader, user)
    
    def ingest_sql(self, path:str, user:User):

        return self.sql_ingestion.run(path, user)
    
    def inference(self, query:str, user:User, chat_history=None, *, test:bool = False):
        chat_history = chat_history or []
        if not all([self.vector_retriever, self.answer]):
            raise ValueError("Pipeline is not fully configured")
        
        docs = self.vector_retriever.run(query, user)

        if test:
            return docs
        return self.answer.run(query, docs, chat_history)
    
    def ingest_schema(self, docs:List[Document]):
        result = self.guidance_store.ingest_schema(docs)
        return result