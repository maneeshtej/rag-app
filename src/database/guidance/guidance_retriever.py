# src/database/guidance/guidance_retriever.py

from src.models.document import RuleChunk, SchemaChunk
from src.models.user import User


class GuidanceRetriever:
    def __init__(self, *, guidance_store, embedder):
        self.guidance_store = guidance_store
        self.embedder = embedder

    def retrieve_query(
        self,
        *,
        query: str,
        user: User,
        type: str,
        k: int = 5,
    ) -> list[RuleChunk]:
        query_embedding = self.embedder.embed_query(query)

        return self.guidance_store.semantic_query_search(
            query_embedding=query_embedding,
            type=type,
            k=k,
        )
    
    def retrieve_schema(
    self,
    *,
    query: str,
    user: User,
    k: int = 5,
    ) -> list[SchemaChunk]:

        query_embedding = self.embedder.embed_query(query)

        primary = self.guidance_store.semantic_schema_search(
            query_embedding=query_embedding,
            k=k,
        )

        related_names: set[str] = set()

        for chunk in primary:
            related_names.update(chunk.related_tables)

        primary_names = {c.name for c in primary}
        related_names -= primary_names

        if not related_names:
            return primary

        related = self.guidance_store.fetch_schema_by_names(
            names=list(related_names)
        )

        merged: dict[str, SchemaChunk] = {c.name: c for c in primary}
        for c in related:
            merged.setdefault(c.name, c)

        return list(merged.values())

