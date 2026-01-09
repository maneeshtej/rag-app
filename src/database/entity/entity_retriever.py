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
        """
        Perform embedding-based similarity search for multiple queries.

        Input Shape
        -----------
        queries : list[dict]
            [
                {
                    "surface_form": str,
                    "entity_type": str
                }
            ]

        Parameters
        ----------
        soft_k : int
            Number of top results to always include regardless of similarity.
        hard_k : int
            Maximum number of results to fetch from the vector store.
        threshold : float
            Minimum similarity score required for inclusion
            beyond the soft_k cutoff.

        Behavior
        --------
        - Embeds each surface_form
        - Searches the entity_embeddings table for nearest vectors
        - Applies soft/hard filtering
        - Hydrates matched entity rows from their source tables

        Returns
        -------
        list[dict]
            [
                {
                    "surface_form": str,
                    "entity_type": str,
                    "resolved": [
                        {
                            "entity": tuple,        # DB row
                            "similarity": float,
                            "source_table": str
                        }
                    ]
                }
            ]
        """

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
        """
            Perform raw vector similarity search.

            Input
            -----
            entity_type : str
                Logical entity type to constrain search.
            embedding : list[float]
                Vector representation of the query surface form.
            hard_k : int
                Maximum number of nearest neighbors to retrieve.

            Behavior
            --------
            - Queries entity_embeddings using cosine distance
            - Orders by closest vectors
            - Limits results to hard_k

            Returns
            -------
            list[tuple]
                [
                    (entity_id, source_table, similarity_score)
                ]
            """

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
        """
        Apply soft-k and similarity threshold filtering.

        Input
        -----
        rows : list[tuple]
            [
                (entity_id, source_table, similarity)
            ]

        Behavior
        --------
        - Always keeps the first soft_k results
        - Keeps additional results only if similarity >= threshold
        - Stops processing once threshold condition fails

        Returns
        -------
        list[tuple]
            Filtered list of (entity_id, source_table, similarity)
        """

        out = []
        for i, (entity_id, source_table, similarity) in enumerate(rows):
            if i < soft_k or similarity >= threshold:
                out.append((entity_id, source_table, similarity))
            else:
                break
        return out

    def _hydrate(self, rows):
        """
        Fetch full database records for matched entity IDs.

        Input
        -----
        rows : list[tuple]
            [
                (entity_id, source_table, similarity)
            ]

        Behavior
        --------
        - Groups entity IDs by source table
        - Fetches full rows from each table
        - Attaches similarity score and source table metadata

        Returns
        -------
        list[dict]
            [
                {
                    "entity": tuple,         # full DB row
                    "similarity": float,
                    "source_table": str
                }
            ]
        """

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
