# src/pipelines/vector_ingestion.py

from uuid import UUID, uuid4
from typing import List
from langchain_core.documents import Document
from src.database.db import get_dev_connection
from src.database.dependencies import create_embedder
from src.database.vector.vector_store import VectorStore
from src.models.document import StoredChunk, StoredFile


class VectorIngestor:
    def __init__(self, vector_store: VectorStore, embedder):
        self.store = vector_store
        self.embedder = embedder

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

        chunks: list[StoredChunk] = []

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
            self.store.commit()
        except Exception:
            self.store.rollback()
            raise

        return True

# main.py

from langchain_community.document_loaders import TextLoader, PyPDFLoader
from src.database.vector.vector_store import VectorStore

from uuid import uuid4

def main():
    # loader = TextLoader("data/sample.txt")
    loader = PyPDFLoader("test_long.pdf")
    conn = get_dev_connection()
    
    docs = loader.load()

    # attach required metadata
    for d in docs:
        d.metadata.update({
            "owner_id": str(uuid4()),
            "role": "user",
            "access_level": "private",
            "source": "text_file"
        })

    vector_store = VectorStore(conn=conn)
    embedder = create_embedder()

    ingestor = VectorIngestor(vector_store=vector_store, embedder=embedder)
    try:
        result = ingestor.ingest_documents(docs=docs)
        conn.commit()
    except Exception as e:
        raise e

    print("Ingestion complete")

if __name__ == "__main__":
    main()
