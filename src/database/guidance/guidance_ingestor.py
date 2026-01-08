from src.models.guidance import GuidanceIngest


class GuidanceIngestor:
    def __init__(self, guidance_store, embedder):
        self.guidance_store = guidance_store
        self.embedder = embedder

    def ingest(self, *, rules: list[dict]) ->  list[GuidanceIngest]:
        items: list[GuidanceIngest] = []

        for r in rules:
            embedding_text = r.get("embedding_text", "").strip()
            embedding = self.embedder.embed_query(embedding_text)

            items.append(
                GuidanceIngest(
                    name=r["name"],
                    type=r["type"],
                    priority=r.get("priority", 0),
                    content=r["content"].strip(),
                    embedding_text=embedding_text,
                    embedding=embedding,
                )
            )

        return self.guidance_store.ingest(items=items)
    
    def truncate(self):
        return self.guidance_store.truncate()
