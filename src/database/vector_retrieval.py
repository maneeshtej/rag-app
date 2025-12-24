from database.vector_store import VectorStore
from models.user import User


class VectorRetriever:
    def __init__(self, vectorstore, embedder):
        self.vectorstore: VectorStore = vectorstore
        self.embedder = embedder

    def retrieve(self, query:str, user:User, k:int = 5):
        if not query:
            return []
        
        query_embedding = self.embedder.embed_query(query)

        return self.vectorstore.similarity_search(
            query_embedding=query_embedding,
            k=k,
            owner_id= user.id,
            min_access_level=user.access_level
        )
    
    def list_files(self, user: User):
        return self.vectorstore.list_files(user=user)
    
    def delete_file(self, source:str):
        return self.vectorstore.delete_file(source)