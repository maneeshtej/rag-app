from src.database.entity.entity_store import EntityStore


class EntityRetriever:
    def __init__(self, *, entity_store, embedder):
        self.entity_store:EntityStore = entity_store
        self.embedder = embedder
        self.version = "0.0.4"

    def retrieve(
        self,
        queries: dict | list[dict],
        *,
        soft_k: int = 3,
        hard_k: int = 5,
        threshold: float = 0.7,
    ) -> list[dict]:
        """
        Resolve entity surface forms using vector similarity search.

        Input
        -----
        queries : dict | list[dict]

        Accepted shapes:

        Single entity:
        {
            "entity_type": str,      # e.g. "teacher"
            "surface_form": str,     # raw text from query
            "op": str                # optional comparison operator
        }

        Multiple entities:
        [
            {
                "entity_type": str,
                "surface_form": str,
                "op": str
            }
        ]

        Behavior
        --------
        - Normalizes input to a list internally
        - Performs similarity search per entity
        - Adds `resolved` field in-place

        Output Mutation
        ---------------
        Each entity dict gains:
        "resolved": [
            {entity_id, surface_form, source_table, source_column, similarity_score},
            ...
        ]

        Returns
        -------
        Same shape as input (dict in → dict out, list in → list out)
        """

        is_single = isinstance(queries, dict)
        query_list = [queries] if is_single else queries

        for q in query_list:
            surface_form = q["surface_form"]
            entity_type = q["entity_type"]

            embedding = self.embedder.embed_query(surface_form)

            rows = self._similarity_search(entity_type, embedding, hard_k)
            filtered = self._apply_soft_hard(rows, soft_k, threshold)

            q["resolved"] = filtered

        return query_list




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
            surface_form,
            source_table,
            source_column,
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
        Returns structured resolved entities.
        """

        out = []

        for i, (entity_id, surface_form, source_table, source_column, similarity) in enumerate(rows):
            if i < soft_k or similarity >= threshold:
                out.append({
                    "entity_id": entity_id,
                    "surface_form": surface_form,
                    "source_table": source_table,
                    "source_column": source_column,
                    "similarity": similarity
                })
            else:
                break

        return out


