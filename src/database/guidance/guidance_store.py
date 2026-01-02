# src/database/guidance/guidance_store.py

import json

from sqlalchemy import Null, null
from src.models.document import RuleChunk, SchemaChunk


class GuidanceStore:
    def __init__(self, *, conn):
        self.conn = conn

    def insert_schema_chunks(self, *, schema_chunks: list[SchemaChunk]) -> int:

        if not schema_chunks:
            return 0

        query = """
        INSERT INTO schema_rules (name, content, schema, related_tables, embedding)
        VALUES (%s, %s, %s, %s, %s)
        """

        with self.conn.cursor() as cur:
            for chunk in schema_chunks:
                cur.execute(
                    query,
                    (
                        chunk.name,
                        chunk.content,
                        json.dumps(chunk.schema),
                        chunk.related_tables,
                        chunk.embedding
                    )
                )


        return len(schema_chunks)

    def insert_rule_chunks(self, *, rule_chunks: list[RuleChunk]) -> int:
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
    
    def truncate_query_rules(self):
        query = "TRUNCATE TABLE query_rules"

        with self.conn.cursor() as cur:
            cur.execute(query)

    def truncate_schema_rules(self):
        query = "TRUNCATE TABLE schema_rules"

        with self.conn.cursor() as cur:
            cur.execute(query)

    def semantic_query_search(
        self,
        *,
        query_embedding: list[float],
        type: str,
        k: int,
    ) -> list[RuleChunk]:

        sql = """
            SELECT
                name,
                content,
                priority,
                type,
                1 - (embedding <=> %s::vector) AS similarity
            FROM query_rules
            WHERE embedding IS NOT NULL
            AND type = %s
            ORDER BY similarity DESC
            LIMIT %s
        """

        with self.conn.cursor() as cur:
            cur.execute(sql, (query_embedding, type, k))
            rows = cur.fetchall()

        return [
            RuleChunk(
                name=row[0],
                content=row[1],
                priority=row[2],
                type=row[3],
                similarity=row[4]
            )
            for row in rows
        ]
    
    def semantic_schema_search(
    self,
    *,
    query_embedding: list[float],
    k: int = 5
) -> list[SchemaChunk]:

        query = """
        SELECT 
            name,
            content,
            schema,
            related_tables,
            1 - (embedding <=> %s::vector) AS similarity
        FROM schema_rules
        WHERE embedding IS NOT NULL
        ORDER BY similarity DESC
        LIMIT %s
        """

        with self.conn.cursor() as cur:
            cur.execute(
                query,
                (
                    query_embedding,
                    k,
                )
            )
            rows = cur.fetchall()

        return [
            SchemaChunk(
                name=row[0],
                content=row[1],
                schema=row[2],
                related_tables=row[3],
                similarity=row[4],
            )
            for row in rows
        ]
    
    def fetch_schema_by_names(
    self,
    *,
    names: list[str],
) -> list[SchemaChunk]:

        sql = """
            SELECT
                name,
                content,
                schema,
                related_tables,
                NULL AS similarity
            FROM schema_rules
            WHERE name = ANY(%s)
        """

        with self.conn.cursor() as cur:
            cur.execute(sql, (names,))
            rows = cur.fetchall()

        return [
            SchemaChunk(
                name=row[0],
                content=row[1],
                schema=row[2],
                related_tables=row[3],
                similarity= None,
            )
            for row in rows
        ]


