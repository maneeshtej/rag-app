# src/pipelines/vector_ingestion.py

from uuid import UUID, uuid4
from typing import List
from langchain_core.documents import Document
from src.database.vector.vector_store import VectorStore
from src.models.document import StoredChunk, StoredFile


class VectorIngestor:
    def __init__(self, vector_store: VectorStore, embedder, conn):
        self.store = vector_store
        self.embedder = embedder
        self.conn = conn

    def ingest_documents(self, docs: List[Document], type: str = "vector"):
        if not docs:
            return "no_docs"

        meta = docs[0].metadata
        file_id = uuid4()

        stored_file = StoredFile(
            id=file_id,
            owner_id=UUID(meta["owner_id"]),
            role=meta["role"],
            access_level=meta["access_level"],
            source=meta.get("source"),
        )

        texts = [d.page_content for d in docs]
        embeddings = self.embedder.embed_documents(texts)

        chunks = [
            StoredChunk(
                id=uuid4(),
                file_id=file_id,
                content=doc.page_content,
                embedding=emb,
                metadata=doc.metadata or {},
            )
            for doc, emb in zip(docs, embeddings)
        ]

        try:
            self.store.insert_file(stored_file)
            self.store.insert_chunks(chunks, type=type)
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

        return "success"
