from datetime import datetime
from typing import List
from uuid import UUID, uuid4
from src.models.user import User
from langchain_core.documents import Document


class VectorIngestion:
    def __init__(self, splitter=None, vectorstore=None):
        self.splitter = splitter
        self.vectorstore = vectorstore

    def set_splitter(self, splitter):
        self.splitter = splitter
        return self

    def set_vectorstore(self, vectorstore):
        self.vectorstore = vectorstore
        return self

    def run(self, loader, user: User):
        if not all([self.splitter, self.vectorstore]):
            raise ValueError("IngestionPipeline is not fully configured")

        docs: List[Document] = loader.load()
        for doc in docs:
            doc.metadata = {
                "owner_id":user.id,
                "role": user.role,
                "access_level": user.access_level,
                "source": doc.metadata.get("source"),
            }


        chunks: List[Document] = self.splitter.split_documents(docs)

        output = self.vectorstore.add_documents(chunks)
        return output
    


