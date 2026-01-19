from src.database.vector.vector_store import VectorStore
from src.models.guidance import GuidanceIngest
from src.models.user import User


class VectorRetriever:
    def __init__(self, vector_store:VectorStore, min_similarity:int = 0.60):
        self.vector_store = vector_store
        self.min_similarity = min_similarity

    def retrieve(self, query_embedding, user:User, k=5):
        if not query_embedding:
            raise ValueError("empty query embedding")

        chunks = self.vector_store.similarity_search(
            query_embedding=query_embedding,
            k=k,
            min_access_level=user.access_level,
        )

        if not chunks or chunks[0].similarity < self.min_similarity:
            return []
        
        actual_chunks:list[GuidanceIngest] = []
        
        for chunk in chunks:
            if chunk.access_level <= user.access_level:
                actual_chunks.append(chunk)

        return [c for c in actual_chunks if c.similarity >= self.min_similarity]
