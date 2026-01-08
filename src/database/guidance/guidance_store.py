import json
from psycopg2.extras import execute_values

from src.models.guidance import GuidanceIngest

class GuidanceStore:
    def __init__(self, *, conn):
        self.conn = conn

    def truncate(self):
        query = """
        TRUNCATE TABLE guidance, guidance_embeddings CASCADE
        """
        with self.conn.cursor() as cur:
            cur.execute(query)

    def ingest(self, *, items: list[GuidanceIngest]) -> list[GuidanceIngest]:
        with self.conn.cursor() as cur:
            # 1. prepare db objects
            guidance_objects = [i.to_db_dict() for i in items]

            # 2. insert guidance (idempotent)
            cur.execute(
                """
                INSERT INTO guidance (name, type, priority, content, active)
                SELECT x.name, x.type, x.priority, x.content, x.active
                FROM jsonb_to_recordset(%s::jsonb) AS
                x(name TEXT, type TEXT, priority INT, content TEXT, active BOOLEAN)
                """,
                (json.dumps(guidance_objects),)
            )

            # 3. fetch ALL ids for these names
            cur.execute(
                """
                SELECT id, name
                FROM guidance
                WHERE name = ANY(%s)
                """,
                ([i.name for i in items],)
            )

            id_map = {name: gid for gid, name in cur.fetchall()}

            # 4. attach ids to objects
            for i in items:
                i.id = id_map[i.name]

            # 5. insert embeddings
            embed_rows = [
                (i.id, i.embedding, i.embedding_text, True)
                for i in items
                if i.embedding and i.embedding_text
            ]

            if embed_rows:
                execute_values(
                    cur,
                    """
                    INSERT INTO guidance_embeddings
                    (guidance_id, embedding, embedding_text, active)
                    VALUES %s
                    """,
                    embed_rows
                )

        return items


    def similarity_search(
        self,
        *,
        query_embedding: list[float],
        type: str,
        k: int = 5
    ) -> list[GuidanceIngest]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    g.id,
                    g.name,
                    g.type,
                    g.priority,
                    g.content,
                    ge.embedding <-> %s::vector AS distance
                FROM guidance_embeddings ge
                JOIN guidance g ON g.id = ge.guidance_id
                WHERE g.type = %s
                AND g.active = true
                AND ge.active = true
                ORDER BY ge.embedding <-> %s::vector
                LIMIT %s
                """,
                (query_embedding, type, query_embedding, k)
            )
            rows = cur.fetchall()

        results: list[GuidanceIngest] = []

        for gid, name, gtype, priority, content, distance in rows:
            similarity = 1.0 / (1.0 + float(distance))

            gi = GuidanceIngest(
                id=gid,
                name=name,
                type=gtype,
                priority=priority,
                content=content,
                similarity=similarity,
            )
            results.append(gi)

        return results



