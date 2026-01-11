class EntityResolver:
    def __init__(
        self,
        *,
        entity_retriever,
        sql_ingestor,
        entity_ingestor,
    ):
        self.entity_retriever = entity_retriever
        self.sql_ingestor = sql_ingestor
        self.entity_ingestor = entity_ingestor

    def resolve(self, payload: dict):
        """
        Entry point.
        Resolves entities and ingests unresolved ones.
        """

        resolved_items = self._resolve_only(payload)
        print(f"\n\nResolved: \n\n{resolved_items}")
        self._ingest_unresolved(payload, resolved_items)

        return resolved_items

    def _resolve_only(self, payload: dict):
        rows = payload["rows"]
        entity_type = payload["entity_type"]

        queries = []
        for row in rows:
            queries.append({
                "surface_form": self._build_surface_form(row),
                "entity_type": entity_type
            })

        results = self.entity_retriever.retrieve(
            queries=queries,
            soft_k=0,
            hard_k=1
        )

        return [
            {
                "row": row,
                "surface_form": q["surface_form"],
                "resolved": r["resolved"],
            }
            for row, q, r in zip(rows, queries, results)
        ]

    # -------------------------
    # Step 2: ingest unresolved
    # -------------------------
    def _ingest_unresolved(self, payload: dict, resolved_items: list[dict]):
        table = payload["table"]
        entity_type = payload["entity_type"]

        to_embed = []

        for item in resolved_items:
            # already resolved → skip
            if item["resolved"]:
                continue

            entity_id = self._insert_row(
                table=table,
                row=item["row"]
            )

            embedding_texts = self._build_embedding_texts(
            item["surface_form"]
            )

            to_embed.append({
                "entity_type": entity_type,
                "entity_id": entity_id,
                "surface_form": item["surface_form"],
                "source_table": table,
                "embedding_text": embedding_texts})
        print(f"\n\nTo embed: {to_embed}")

        if to_embed:
            self.entity_ingestor.ingest(to_embed)

    # -------------------------
    # Step 2a: insert business row
    # -------------------------
    def _insert_row(self, *, table: str, row: dict) -> str:
        sql_obj = {
            "action": "insert",
            "table": table,
            "data": row,
            "returning": "id",
        }

        result = self.sql_ingestor.ingest(sql_obj=sql_obj)
        return result[0][0]

    # -------------------------
    # Utility: surface form
    # -------------------------
    def _build_surface_form(self, row: dict) -> str:
        return " ".join(
            str(v)
            for v in row.values()
            if v not in (None, "", [])
        )
    
    def _build_embedding_texts(self, surface_form: str) -> list[str]:
        """
        Generate multiple textual variants for embedding.
        """
        base = surface_form.strip()

        parts = base.split()

        variants = set()
        variants.add(base)

        # lowercase / uppercase
        variants.add(base.lower())
        variants.add(base.title())

        # individual tokens
        for p in parts:
            variants.add(p)
            variants.add(p.lower())
            variants.add(p.title())

        # remove titles
        titles = {"dr", "prof", "mr", "ms", "mrs"}
        filtered = [p for p in parts if p.lower().strip(".") not in titles]
        if filtered:
            variants.add(" ".join(filtered))
            variants.add(" ".join(filtered).lower())
            variants.add(" ".join(filtered).title())

        return list(variants)

