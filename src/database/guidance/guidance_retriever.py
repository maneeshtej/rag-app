# src/database/guidance/guidance_retriever.py

from src.models.user import User


class GuidanceRetriever:
    def __init__(self, *, guidance_store, embedder):
        self.guidance_store = guidance_store
        self.embedder = embedder

    def retrieve(
        self,
        *,
        query: str,
        user: User,
        type: str,
        k: int = 5,
    ):
        query_embedding = self.embedder.embed_query(query)

        return self.guidance_store.semantic_search(
            query_embedding=query_embedding,
            type=type,
            k=k,
        )
