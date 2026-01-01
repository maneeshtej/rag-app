from src.models.user import User


class GuidanceRetriever:

    def __init__(self, *, guidance_retriever):
        self.guidance_store = guidance_retriever

    def retrieve(self, *, query:str, user:User, type:str):
        return self.guidance_store.semantic_search()