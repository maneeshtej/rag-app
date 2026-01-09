class EntityRetriever:
    def __init__(self, *, entity_store, embedder):
        self.entity_store = entity_store
        self.embedder = embedder

    def retrieve(
        self,
        queries: list[dict],
        *,
        soft_k: int = 3,
        hard_k: int = 5,
        threshold: float = 0.7,
    ) -> list[dict]:

        output = []

        for q in queries:
            surface_form = q["surface_form"]
            entity_type = q["entity_type"]

            embedding = self.embedder.embed_query(surface_form)

            rows = self._similarity_search(entity_type, embedding, hard_k)
            filtered = self._apply_soft_hard(rows, soft_k, threshold)
            hydrated = self._hydrate(filtered)

            output.append({
                "surface_form": surface_form,
                "entity_type": entity_type,
                "resolved": hydrated
            })

        return output


    def _similarity_search(self, entity_type, embedding, hard_k):
        sql = """
        SELECT
            entity_id,
            source_table,
            1 - (embedding <=> %s::vector) AS similarity
        FROM entity_embeddings
        WHERE entity_type = %s
        ORDER BY embedding <=> %s::vector
        LIMIT %s
        """
        return self.entity_store.execute_read(
            sql, (embedding, entity_type, embedding, hard_k)
        )

    def _apply_soft_hard(self, rows, soft_k, threshold):
        out = []
        for i, (entity_id, source_table, similarity) in enumerate(rows):
            if i < soft_k or similarity >= threshold:
                out.append((entity_id, source_table, similarity))
            else:
                break
        return out

    def _hydrate(self, rows):
        by_table = {}
        for entity_id, table, similarity in rows:
            by_table.setdefault(table, []).append((entity_id, similarity))

        results = []
        for table, items in by_table.items():
            ids = [eid for eid, _ in items]
            sql = f"SELECT * FROM {table} WHERE id = ANY(%s::uuid[])"
            records = self.entity_store.execute_read(sql, (ids,))
            record_map = {r[0]: r for r in records}

            for entity_id, similarity in items:
                if entity_id in record_map:
                    results.append({
                        "entity": record_map[entity_id],
                        "similarity": similarity,
                        "source_table": table,
                    })
        return results
