# src/database/vector_store.py

import json
from uuid import UUID
from typing import List
from langchain_core.documents import Document
from src.models.document import StoredChunk, StoredFile
from src.models.user import User


class VectorStore:
    def __init__(self, conn):
        self.conn = conn
    # ---------- FILES ----------

    def insert_file(self, file: StoredFile):
        query = """
        INSERT INTO files (id, owner_id, role, access_level, source)
        VALUES (%s, %s, %s, %s, %s)
        """
        with self.conn.cursor() as cur:
            cur.execute(
                query,
                (
                    str(file.id),
                    str(file.owner_id),
                    file.role,
                    file.access_level,
                    file.source,
                )
            )

    def list_files(self, user: User) -> List[StoredFile]:
        query = """
        SELECT id, owner_id, role, access_level, source
        FROM files
        WHERE (%s IS NULL OR owner_id = %s)
        ORDER BY created_at DESC
        """

        with self.conn.cursor() as cur:
            cur.execute(query, (user.id, user.id))
            rows = cur.fetchall()

        return [
            StoredFile(
                id=row[0],
                owner_id=row[1],
                role=row[2],
                access_level=row[3],
                source=row[4],
            )
            for row in rows
        ]

    def delete_file(self, source: str) -> int:
        query = "DELETE FROM files WHERE source = %s"

        with self.conn.cursor() as cur:
            cur.execute(query, (source,))
            deleted = cur.rowcount

        return deleted

    # ---------- CHUNKS ----------

    def insert_chunks(self, chunks: List[StoredChunk], type: str = "vector"):
        query = """
        INSERT INTO vector_chunks (id, file_id, content, embedding, metadata, type)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        with self.conn.cursor() as cur:
            for chunk in chunks:
                cur.execute(
                    query,
                    (
                        str(chunk.id),
                        str(chunk.file_id),
                        chunk.content,
                        chunk.embedding,
                        json.dumps(chunk.metadata),
                        type,
                    )
                )

    # ---------- RETRIEVAL ----------

    def similarity_search(
        self,
        query_embedding: list[float],
        k: int,
        min_access_level: int,
        type: str = "vector",
    ) -> List[Document]:
        query = """
        SELECT 
            c.id,
            c.content,
            c.metadata,
            f.id,
            f.owner_id,
            f.role,
            f.source,
            f.access_level,
            1 - (c.embedding <=> %s::vector) AS similarity
        FROM vector_chunks c
        JOIN files f ON c.file_id = f.id
        WHERE f.access_level >= %s
          AND c.type = %s
        ORDER BY similarity DESC
        LIMIT %s
        """

        with self.conn.cursor() as cur:
            cur.execute(
                query,
                (query_embedding, min_access_level, type, k),
            )
            rows = cur.fetchall()

        documents = []
        for row in rows:
            meta = row[2] or {}
            if isinstance(meta, str):
                meta = json.loads(meta)

            documents.append(
                Document(
                    page_content=row[1],
                    metadata={
                        **meta,
                        "chunk_id": str(row[0]),
                        "file_id": str(row[3]),
                        "owner_id": str(row[4]),
                        "role": row[5],
                        "source": row[6],
                        "access_level": row[7],
                        "similarity": row[8],
                    },
                )
            )

        return documents
