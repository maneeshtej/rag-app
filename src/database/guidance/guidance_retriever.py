from src.models.guidance import GuidanceIngest


class GuidanceRetriever:
    def __init__(self, *, guidance_store, embedder):
        self.guidance_store = guidance_store
        self.embedder = embedder

    def retrieve(
        self,
        *,
        query: str,
        type: str,
        soft_k: int = 5,
        hard_k: int = 8,
        min_similarity: float = 0.65,
    ) -> list[GuidanceIngest]:
        query_embedding = self.embedder.embed_query(query)

        candidates = self.guidance_store.similarity_search(
            query_embedding=query_embedding,
            type=type,
            k=hard_k,
        )

        selected: list[GuidanceIngest] = []

        for idx, item in enumerate(candidates):
            # always include top soft_k
            if idx < soft_k:
                selected.append(item)
                continue

            # similarity threshold
            if item.similarity is not None and item.similarity >= min_similarity:
                selected.append(item)

        return selected
