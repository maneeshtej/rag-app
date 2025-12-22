
from uuid import UUID, uuid4
from langchain_core.documents import Document
from typing import List
from models.document import StoredChunk, StoredFile
from models.user import User

class PGVectorStore:
    def __init__(self, embedder, conn):
        self.conn = conn
        self.embedder = embedder

    
    def _doc_to_stored_chunk(
        self,
        doc: Document,
        embedding: list[float]
    ) -> StoredChunk:
        return StoredChunk(
            id=UUID(doc.metadata["id"]) if "id" in doc.metadata else uuid4(),
            content=doc.page_content,
            embedding=embedding,
            owner_id=UUID(doc.metadata["owner_id"]),
            role=doc.metadata["role"],
            access_level=doc.metadata["access_level"],
            source=doc.metadata.get("source"),
        )

    def _stored_chunk_to_doc(self, chunk: StoredChunk) -> Document:
        return Document(
            page_content=chunk.content,
            metadata={
                "id": str(chunk.id),
                "owner_id": str(chunk.owner_id),
                "role": chunk.role,
                "access_level": chunk.access_level,
                "source": chunk.source,
            },
        )
    
    def _insert_file(self, file: StoredFile):
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
    
    def _insert_chunks(self, chunks: List[StoredChunk]):
        query = """
        INSERT INTO vector_chunks (id, file_id, content, embedding)
        VALUES (%s, %s, %s, %s)
        """

        with self.conn.cursor() as cur:
            for chunk in chunks:
                cur.execute(
                    query,
                    (
                        str(chunk.id),
                        str(chunk.file_id),
                        chunk.content,
                        chunk.embedding
                    )
                )

    

    def add_documents(self, docs: List[Document]):
        file_id  = uuid4()
        meta = docs[0].metadata

        stored_file = StoredFile(
            id=file_id,
            owner_id=UUID(meta['owner_id']),
            role=meta['role'],
            access_level=meta['access_level'],
            source=meta.get('source')
        )

        texts = [doc.page_content for doc in docs]
        embeddings = self.embedder.embed_documents(texts)

        stored_chunks = [
            StoredChunk(
                id=uuid4(),
                file_id=file_id,
                content=doc.page_content,
                embedding=emb,
            ) for doc, emb in zip(docs, embeddings)
        ]

        try:
            self._insert_file(stored_file)
            self._insert_chunks(stored_chunks)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
        
        return "success"

    def similarity_search(
        self,
        query_embedding: list[float],
        k: int,
        owner_id: UUID,
        min_access_level: int,
    ) -> List[Document]:
        query = """
        SELECT 
        c.id, c.content, f.id, f.owner_id, f.role, f.source, f.access_level
        FROM vector_chunks c
        JOIN files f on c.file_id = f.id
        WHERE
            f.access_level >= %s
        ORDER BY c.embedding <-> %s::vector
        LIMIT %s
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

        documents = [
            Document(
                page_content=row[1],
                metadata={
                    "chunk_id": str(row[0]),
                    "file_id": str(row[2]),
                    "owner_id": str(row[3]),
                    "role": row[4],
                    "source": row[5],
                    "access_level": row[6],
                },
            )
            for row in rows
        ]

        return documents
    
    def list_files(self, user: User) -> List[StoredFile]:
        owner_id = user.id

        query = """
        SELECT id, owner_id, role, access_level, source
        FROM files
        WHERE (%s IS NULL OR owner_id = %s)
        ORDER BY created_at DESC
        """

        with self.conn.cursor() as cur:
            cur.execute(
                query,
                (
                    owner_id, owner_id
                )
            )

            rows = cur.fetchall()

            stored_files = [
                StoredFile(
                    id=row[0],
                    owner_id=row[1],
                    role=row[2],
                    access_level=row[3],
                    source=row[4]
                ) for row in rows
            ]

            return stored_files
        
    def delete_file(self, source:str):
            query = """
            DELETE FROM files
            WHERE source = %s
            """

            try:
                with self.conn.cursor() as cur:
                    cur.execute(
                        query,
                        (source,)
                    )
                    deleted = cur.rowcount

                    self.conn.commit()
            except Exception as e:
                self.conn.rollback()
                raise e
            if deleted > 0:
                return deleted
            else:
                print("Nothing to delete")



        
    
    