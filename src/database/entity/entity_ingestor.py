class EntityIngestor:
    def __init__(self, *, entity_store, embedder):
        self.entity_store = entity_store
        self.embedder = embedder

    def ingest(self, entities: list[dict]) -> int:
        if not entities:
            return 0

        texts = []
        expanded = []

        for e in entities:
            emb_texts = e.get("embedding_text")

            if isinstance(emb_texts, list):
                for t in emb_texts:
                    texts.append(t)
                    expanded.append({**e, "embedding_text": t})
            else:
                texts.append(e["surface_form"])
                expanded.append({**e, "embedding_text": e["surface_form"]})

        embeddings = self.embedder.embed_documents(texts)

        sql = """
        INSERT INTO entity_embeddings (
            entity_type,
            entity_id,
            surface_form,
            source_table,
            embedding
        )
        VALUES (%s, %s, %s, %s, %s)
        """

        params = [
            (
                e["entity_type"],
                e["entity_id"],
                e["embedding_text"],   # variant text
                e["source_table"],
                emb,
            )
            for e, emb in zip(expanded, embeddings)
        ]

        return self.entity_store.execute_write(sql, params)

