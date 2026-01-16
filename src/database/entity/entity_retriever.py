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

        for q in queries:
            surface_form = q["surface_form"]
            entity_type = q["entity_type"]

            embedding = self.embedder.embed_query(surface_form)

            rows = self._similarity_search(entity_type, embedding, hard_k)
            filtered = self._apply_soft_hard(rows, soft_k, threshold)

            # 🔹 populate in-place
            q["resolved"] = filtered

        return queries



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

