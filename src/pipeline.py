from models.user import User


class MainPipeline:
    def __init__(self, ingestion=None, retriever=None):
        self.ingestion = ingestion
        self.retriever = retriever

    def set_ingestion(self, ingestion):
        self.ingestion = ingestion

    def ingest(self, loader, user:User):
        if not all([self.ingestion]):
            raise ValueError("Pipeline is not fully configured")
        
        return self.ingestion.run(loader, user)
    
    def retrieve(self, query:str, user:User):
        if not self.retrieve:
            raise ValueError("Pipeline is not fully configured")
        
        return self.retriever.run(query, user)