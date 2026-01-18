from typing import List
from langchain_core.documents import Document
from src.models.user import User


class VectorIngestion:
    def __init__(self, *, splitter, ingestor):
        self.splitter = splitter
        self.ingestor = ingestor

    def run(self, loader, user: User):
        if not all([self.splitter, self.ingestor]):
            raise ValueError("VectorIngestion is not fully configured")

        docs: List[Document] = loader.load()

        for doc in docs:
            original_meta = doc.metadata or {}
            doc.metadata = {
                **original_meta,
                "owner_id": str(user.id),
                "role": user.role,
                "access_level": user.access_level,
            }

        chunks: List[Document] = self.splitter.split_documents(docs)

        return self.ingestor.ingest_documents(chunks)
