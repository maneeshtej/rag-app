# src/database/guidance/guidance_store.py

from typing import List
from src.models.document import RuleChunk


class GuidanceStore:
    def __init__(self, *, conn):
        self.conn = conn

    # ---------- INSERT ----------

    def insert_rule_chunks(self, *, rule_chunks: List[RuleChunk]) -> int:
        if not rule_chunks:
            return 0

        query = """
            INSERT INTO query_rules (name, content, priority, type, embedding)
            VALUES (%s, %s, %s, %s, %s)
        """

        with self.conn.cursor() as cur:
            for chunk in rule_chunks:
                cur.execute(
                    query,
                    (
                        chunk.name,
                        chunk.content,
                        chunk.priority,
                        chunk.type,
                        chunk.embedding,
                    )
                )

        return len(rule_chunks)
    
    def truncate(self):
        query = "TRUNCATE TABLE query_rules"

        with self.conn.cursor() as cur:
            cur.execute(query)

    # ---------- SEARCH ----------

    def semantic_search(
        self,
        *,
        query_embedding: list[float],
        type: str,
        k: int,
    ) -> List[RuleChunk]:

        sql = """
            SELECT name, content, priority, type
            FROM query_rules
            WHERE embedding IS NOT NULL
              AND type = %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """

        with self.conn.cursor() as cur:
            cur.execute(sql, (type, query_embedding, k))
            rows = cur.fetchall()

        return [
            RuleChunk(
                name=row[0],
                content=row[1],
                priority=row[2],
                type=row[3],
            )
            for row in rows
        ]
