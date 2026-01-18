import psycopg2
from typing import List, Dict

class ColumnStore:
    def __init__(self, conn):
        self.conn = conn

    def insert_column(
        self,
        *,
        table_name: str,
        column_name: str,
        embedding: list[float],
    ):
        sql = """
        INSERT INTO column_catalog (table_name, column_name, embedding)
        VALUES (%s, %s, %s)
        """
        with self.conn.cursor() as cur:
            cur.execute(sql, (table_name, column_name, embedding))

    def similarity_search(
        self,
        *,
        embedding: list[float],
        table_name: str,
        k: int = 5,
    ) -> List[Dict]:
        """
        Table filter is mandatory.
        Returns candidate columns for a given table.
        """

        sql = """
        SELECT
            table_name,
            column_name,
            1 - (embedding <=> %s) AS similarity
        FROM column_catalog
        WHERE table_name = %s
        ORDER BY embedding <=> %s
        LIMIT %s
        """

        with self.conn.cursor() as cur:
            cur.execute(sql, (embedding, table_name, embedding, k))
            rows = cur.fetchall()

        return [
            {
                "table_name": r[0],
                "column_name": r[1],
                "similarity": float(r[2]),
            }
            for r in rows
        ]
