from models.user import User


class MainPipeline:
    def __init__(self, ingestion=None, retriever=None, answer=None):
        self.ingestion = ingestion
        self.retriever = retriever
        self.answer = answer

    def set_ingestion(self, ingestion):
        self.ingestion = ingestion

    def ingest(self, loader, user:User):
        if not all([self.ingestion]):
            raise ValueError("Pipeline is not fully configured")
        
        return self.ingestion.run(loader, user)
    
    def retrieve(self, query:str, user:User):
        if not self.retriever:
            raise ValueError("Pipeline is not fully configured")
        
        return self.retriever.run(query, user)
    
    def inference(self, query:str, user:User, chat_history=[]):
        if not all([self.retriever, self.answer]):
            raise ValueError("Pipeline is not fully configured")
        
        docs = self.retriever.run(query, user)
        return self.answer.run(query, docs, chat_history)