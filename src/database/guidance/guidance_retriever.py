from src.models.user import User


class GuidanceRetriever:

    def __init__(self, *, guidance_store):
        self.guidance_store = guidance_store

    def retrieve(self, *, query:str, user:User, type:str, k:int=5):
        query_embedding = self.guidance_store.embedder.embed_query(query)
        return self.guidance_store.semantic_search(
            query_embedding=query_embedding,
            user=user,
            type=type,
            k=k
        )