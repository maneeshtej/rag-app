# src/retrieval/vector_retrieval.py

from src.models.user import User
from src.models.retrieved_chunk import RetrievedChunk


class VectorRetrieval:
    def __init__(self, *, retriever, reranker, embedder):
        self.retriever = retriever
        self.reranker = reranker
        self.embedder = embedder

    def __enhance_query(self, *, query: str) -> str:
        return query.strip().lower()

    def __rerank(self, *, chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
        if not chunks:
            return []
        return self.reranker.rerank(chunks)

    def retrieve(
        self,
        *,
        query: str,
        user: User,
        k: int = 5,
    ) -> list[RetrievedChunk]:

        if not query:
            return []

        enhanced_query = self.__enhance_query(query=query)
        query_embedding = self.embedder.embed_query(enhanced_query)

        chunks = self.retriever.retrieve(
            query_embedding=query_embedding,
            user=user,
            k=k,
        )

        if not chunks:
            return []

        return self.__rerank(chunks=chunks)
