from src.database.nl2sql.nl2sql_engine import NL2SQLEngine


class SQLRetriever:
    """
    Dumb SQL executor.
    No LLM.
    No planning.
    No entities.
    No schema logic.
    """

    def __init__(self, *, sql_store):
        self.sql_store = sql_store

    def run(
        self,
        *,
        sql: str,
        params: list | tuple = (),
        limit: int = 100,
    ) -> list[dict]:
        if not sql:
            return []

        return self.sql_store.execute_read(
            sql=sql,
            params=tuple(params),
            limit=limit,
        )

    def get_row(
        self,
        *,
        table: str,
        where: dict,
    ) -> dict | None:
        if not where:
            raise ValueError("where cannot be empty")

        conditions = " AND ".join(f"{k} = %s" for k in where)
        sql = f"SELECT * FROM {table} WHERE {conditions} LIMIT 1"

        rows = self.sql_store.execute_read(
            sql=sql,
            params=tuple(where.values()),
            limit=1,
        )

        return rows[0] if rows else None

