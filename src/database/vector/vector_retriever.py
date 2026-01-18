from datetime import datetime, timezone
from src.database.vector.vector_store import VectorStore
from src.models.retrieved_chunk import RetrievedChunk
from src.models.user import User


class VectorRetriever:
    def __init__(self, vector_store: VectorStore, min_similarity: float):
        self.vector_store = vector_store
        self.min_similarity = min_similarity

    def _freshness_score(self, created_at):
        days = (datetime.now(timezone.utc) - created_at).days
        if days <= 30:
            return 1.0
        if days <= 180:
            return 0.7
        return 0.4

    def _authority_score(self, access_level: int):
        return {
            0: 1.0,  # system
            1: 0.9,  # admin
            2: 0.7,  # internal
            3: 0.5,  # public
        }.get(access_level, 0.5)

    def _score(self, chunk: RetrievedChunk) -> float:
        return (
            chunk.similarity * 0.7 +
            self._freshness_score(chunk.created_at) * 0.2 +
            self._authority_score(chunk.access_level) * 0.1
        )

    def retrieve(
        self,
        query_embedding: list[float],
        user: User,
        k: int = 5,
    ) -> list[RetrievedChunk]:

        if not query_embedding:
            raise ValueError("'query_embedding' is empty")

        chunks = self.vector_store.similarity_search(
            query_embedding=query_embedding,
            k=k,
            min_access_level=user.access_level,
        )

        if not chunks:
            return []

        if chunks[0].similarity < self.min_similarity:
            return []

        filtered = [c for c in chunks if c.similarity >= self.min_similarity]

        # 🔥 rerank here
        return sorted(filtered, key=self._score, reverse=True)
