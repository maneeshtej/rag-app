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
