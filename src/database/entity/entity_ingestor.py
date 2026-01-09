class EntityIngestor:
    def __init__(self, *, entity_store, embedder):
        self.entity_store = entity_store
        self.embedder = embedder

    def ingest(self, entities: list[dict]) -> int:
        if not entities:
            return 0

        texts = [
            e.get("embedding_text", e["surface_form"])
            for e in entities
        ]

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
                e["surface_form"],
                e["source_table"],
                emb,
            )
            for e, emb in zip(entities, embeddings)
        ]

        return self.entity_store.execute_write(sql, params)
