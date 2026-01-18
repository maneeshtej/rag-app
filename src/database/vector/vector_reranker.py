from datetime import datetime, timezone
from src.models.retrieved_chunk import RetrievedChunk


class DeterministicReranker:
    def score(self, chunk: RetrievedChunk) -> float:
        return (
            chunk.similarity * 0.7 +
            self._freshness(chunk.created_at) * 0.2 +
            self._authority(chunk.access_level) * 0.1
        )

    def _freshness(self, created_at):
        days = (datetime.now(timezone.utc) - created_at).days
        if days <= 30:
            return 1.0
        if days <= 180:
            return 0.7
        return 0.4

    def _authority(self, access_level):
        return {
            0: 1.0,
            1: 0.9,
            2: 0.7,
            3: 0.5,
        }.get(access_level, 0.5)

    def rerank(self, chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
        return sorted(chunks, key=self.score, reverse=True)
