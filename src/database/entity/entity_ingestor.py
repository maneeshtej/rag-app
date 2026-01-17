class EntityIngestor:
    def __init__(self, *, entity_store, embedder):
        self.entity_store = entity_store
        self.embedder = embedder

    def ingest(self, entities: list[dict]) -> int:
        """
        Ingest canonical entities into the entity_embeddings table.

        Input shape:
        entities = [
          {
            "entity_type": str,          # e.g. "teacher"
            "entity_id": UUID | str,     # canonical entity id
            "surface_form": str,         # base surface form
            "source_table": str,         # e.g. "teachers"
            "source_column: str,         # e.g. "subject_name"

            # OPTIONAL:
            "embedding_text": str | list[str]
            # If list[str]: multiple embedding variants will be created
            # If missing: surface_form is used as embedding text
          }
        ]
        """
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
            source_column,
            embedding
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        params = [
            (
                e["entity_type"],
                e["entity_id"],
                e["embedding_text"],   # variant text
                e["source_table"],
                e["source_column"],
                emb,
            )
            for e, emb in zip(expanded, embeddings)
        ]

        return self.entity_store.execute_write(sql, params)

