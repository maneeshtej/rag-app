from src.database.vector.vector_store import VectorStore
from src.models.user import User


class VectorRetriever:
    def __init__(self, vector_store, embedder):
        self.vector_store: VectorStore = vector_store
        self.embedder = embedder


    def retrieve(self, query:str, user:User, k:int = 5, type:str = "vector"):
        if not query:
            return []
        
        query_embedding = self.embedder.embed_query(query)

        return self.vector_store.similarity_search(
            query_embedding=query_embedding,
            k=k,
            min_access_level=user.access_level,
            type=type
        )
    
    def list_files(self, user: User):
        return self.vector_store.list_files(user=user)
    
    def delete_file(self, source:str):
        return self.vector_store.delete_file(source)