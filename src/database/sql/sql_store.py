class SQLStore:
    def __init__(self, conn):
        self.conn = conn

    def execute_read(self, sql: str, params: tuple | None = None, limit: int = 100) -> list[dict]:
        """Execute SELECT queries only"""

        sql_lower = sql.strip().lower()

        if not sql_lower.startswith("select"):
            raise ValueError("Only SELECT allowed")
        
        if "limit" not in sql_lower and not sql_lower.endswith("limit"):
            sql = f"{sql.rstrip(';')} limit {limit}"

        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, params or ())
                columns = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
        except Exception as e:
            raise RuntimeError(e)
        
        return [dict(zip(columns, row)) for row in rows]

    def close(self):
        try:
            self.conn.close()
        except Exception as e:
            pass

    def resolve_entity(
        self,
        *,
        table: str,
        columns: list[str],
        value: str,
        k: int = 5
    ) -> list[dict]:
        """
        Generic entity resolver.
        Performs ILIKE search across given columns and returns top-k rows.
        """

        if not columns:
            raise ValueError("columns must not be empty")

        # Build OR conditions safely
        conditions = " OR ".join(
            f"{col} ILIKE %s" for col in columns
        )

        sql = f"""
            SELECT *
            FROM {table}
            WHERE {conditions}
            LIMIT %s
        """

        params = [f"%{value}%"] * len(columns)
        params.append(k)

        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]

        return [
            dict(zip(colnames, row))
            for row in rows
        ]
