class EntityResolver:
    def __init__(self, *, entity_retriever):
        self.entity_retriever = entity_retriever

    def resolve(self, payload: dict):
        """
        Resolve entities for a batch of rows belonging to the same table/type.

        Input Shape
        -----------
        payload : dict
            {
                "table": str,
                "entity_type": str,
                "rows": list[dict]
            }

        Where:
        - table       : database table name (e.g. "subjects", "teachers")
        - entity_type : logical entity type used for embeddings
                        (e.g. "subject", "teacher", "class")
        - rows        : list of dictionaries where each dictionary
                        represents a DB-shaped row (no id field)

        Behavior
        --------
        - For each row:
            - Concatenates all non-empty column values into a surface string
            - Sends the surface string to EntityRetriever for similarity search
        - Uses soft_k=0 and hard_k=1 for deterministic lookup

        Returns
        -------
        list[dict]
            [
                {
                    "row": dict,                 # original input row
                    "surface_form": str,         # concatenated text
                    "resolved": list[dict]       # hydrated DB matches
                }
            ]

        Notes
        -----
        - This function does NOT insert or update database rows
        - It only performs retrieval and returns candidates
        """
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
                "resolved": r["resolved"]
            }
            for row, q, r in zip(rows, queries, results)
        ]

    def _build_surface_form(self, row):
        """
        Build a surface form string from a DB-shaped row.

        Input Shape
        -----------
        row : dict
            {
                <column_name>: <value>,
                ...
            }

        Behavior
        --------
        - Iterates over all values in the row
        - Filters out None, empty strings, and empty lists
        - Converts remaining values to strings
        - Concatenates them using a single space

        Returns
        -------
        str
            A flattened textual representation of the row suitable
            for embedding and similarity search.

        Example
        -------
        Input:
            {
                "subject_code": "22CS71",
                "subject_name": "High Performance Computing"
            }

        Output:
            "22CS71 High Performance Computing"
        """
        return " ".join(
            str(v) for v in row.values()
            if v not in (None, "", [])
        )
