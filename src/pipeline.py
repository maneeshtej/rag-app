from models.user import User

class MainPipeline:
    def __init__(self, vector_ingestion, sql_ingestion, vector_retriever, answer):
        self.vector_ingestion = vector_ingestion
        self.sql_ingestion = sql_ingestion
        self.vector_retriever = vector_retriever
        self.answer = answer

    def ingest_vector(self, loader, user:User):
        if not all([self.vector_ingestion]):
            raise ValueError("Pipeline is not fully configured")
        
        return self.vector_ingestion.run(loader, user)
    
    def ingest_sql(self, path:str, user:User):

        return self.sql_ingestion.run(path, user)
    
    def inference(self, query:str, user:User, chat_history=None):
        chat_history = chat_history or []
        if not all([self.vector_retriever, self.answer]):
            raise ValueError("Pipeline is not fully configured")
        
        docs = self.vector_retriever.run(query, user)
        return self.answer.run(query, docs, chat_history)