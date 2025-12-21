
from uuid import UUID, uuid4
from langchain_core.documents import Document
from typing import List
from models.document import MinimalDocument, StoredChunk

class PGVectorStore:
    def __init__(self, embedder, conn):
        self.conn = conn
        self.embedder = embedder

    def add_documents(self, docs:List[Document]):
        texts = [d.page_content for d in docs]
        embeddings = self.embedder.embed_documents(texts)

        chunks = []
        for doc, emb in zip(docs, embeddings):
            chunks.append(
                StoredChunk(
                    id=uuid4(),
                    content=doc.page_content,
                    embedding=emb,
                    owner_id=doc.metadata["owner_id"],
                    role=doc.metadata["role"],
                    access_level=doc.metadata["access_level"],
                    source=doc.metadata.get("source"),
                )
            )

        return self._insert_chunks(chunks)
    
    def _insert_chunks(self, chunks: List[StoredChunk]):
        query = """
         INSERT INTO documents (
                        id, content, embedding,
                        owner_id, role, access_level, source
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        with self.conn.cursor() as cur:
            for c in chunks:
                cur.execute(
                    query,
                    (
                        str(c.id),
                        c.content,
                        c.embedding,
                        str(c.owner_id),
                        c.role,
                        c.access_level,
                        c.source,

                    )
                )
        self.conn.commit()

        return "successs"
    
    def similarity_search(
            self, 
            query_embedding: list[float],
            k:int, 
            owner_id:UUID, 
            min_access_level:int
    ) -> List[StoredChunk]:
        query = """
        SELECT
            id,
            content,
            source
        FROM documents
        WHERE access_level >= %s
        ORDER BY embedding <-> %s::vector
        LIMIT %s;
        """

        with self.conn.cursor() as cur:
            cur.execute(
                query,
                (
                    min_access_level,
                    query_embedding,
                    k,
                )
            )
            rows = cur.fetchall()

        results:List[StoredChunk] = []

        for row in rows:
            results.append(
                MinimalDocument(
                    id=row[0],
                    content=row[1],
                    source=row[2]
                )
            )
        
        return results

        
    
    