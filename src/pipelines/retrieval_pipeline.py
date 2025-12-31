from typing import Dict, List
from database.sql_retriever import SQLRetriever
from database.vector_retriever import VectorRetriever
from src.models.user import User
from src.schema.schema import SCHEMA_MAP, SCHEMA_EXTENSION
from langchain_core.documents import Document


class RetrievalPipeline:
    def __init__(
        self,
        vector_retriever: VectorRetriever,
        sql_retriever: SQLRetriever
    ):
        self.vector_retriever = vector_retriever
        self.sql_retriever = sql_retriever

    def _get_vector_results(
        self, query: str, user: User, k: int
    ) -> List[Document]:
        results =  self.vector_retriever.retrieve(
            query=query,
            user=user,
            k=k,
        )

        print(f"""Results\n\n""")

        for result in results:
            print(f"{[result.metadata.get('source'), result.metadata.get('table_name', 'vector'), result.metadata.get('similarity')]}")
        
        return results


    def run(self, query: str, user: User, k: int = 5, top_n: int = 4):
        if not self.vector_retriever:
            raise ValueError("Pipeline dependencies not initialised")

        vector_chunks = self._get_vector_results(query, user, k)

        return vector_chunks
