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

    def ingest_documents(self, docs: List[Document]) -> bool:
        if not docs:
            return False

        required = {"owner_id", "role", "access_level"}
        for d in docs:
            if not d.metadata or not required.issubset(d.metadata):
                raise ValueError("Missing required metadata for ingestion")

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

        chunks = []
        for doc, emb in zip(docs, embeddings):
            clean_meta = {
                k: v
                for k, v in (doc.metadata or {}).items()
                if k not in {"owner_id", "role", "access_level"}
            }

            chunks.append(
                StoredChunk(
                    id=uuid4(),
                    file_id=file_id,
                    content=doc.page_content,
                    embedding=emb,
                    metadata=clean_meta,
                )
            )

        try:
            self.store.insert_file(stored_file)
            self.store.insert_chunks(chunks)
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

        return True
