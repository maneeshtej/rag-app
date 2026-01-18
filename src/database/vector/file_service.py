# src/services/file_service.py

from typing import List
from src.database.vector.vector_store import VectorStore
from src.models.document import StoredFile
from src.models.user import User


class FileService:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    def list_files(self, user: User) -> List[StoredFile]:
        return self.vector_store.list_files(user=user)

    def delete_file_by_source(self, source: str) -> int:
        return self.vector_store.delete_file(source=source)
