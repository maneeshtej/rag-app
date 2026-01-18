class VectorRetriever:
    def __init__(self, vector_store, min_similarity):
        self.vector_store = vector_store
        self.min_similarity = min_similarity

    def retrieve(self, query_embedding, user, k=5):
        if not query_embedding:
            raise ValueError("empty query embedding")

        chunks = self.vector_store.similarity_search(
            query_embedding=query_embedding,
            k=k,
            min_access_level=user.access_level,
        )

        if not chunks or chunks[0].similarity < self.min_similarity:
            return []

        return [c for c in chunks if c.similarity >= self.min_similarity]
