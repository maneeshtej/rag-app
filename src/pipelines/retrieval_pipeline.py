import json
import re
from src.database.sql.sql_retriever import SQLRetriever
from src.database.vector.vector_retriever import VectorRetriever
from src.models.user import User
from langchain_core.documents import Document


class RetrievalPipeline:
    def __init__(
        self,
        vector_retriever: VectorRetriever,
        sql_retriever: SQLRetriever,
        routing_llm
    ):
        self.vector_retriever = vector_retriever
        self.sql_retriever = sql_retriever
        self.routing_llm = routing_llm



    def _get_vector_results(
        self, query: str, user: User, k: int
    ) -> list[Document]:
        results =  self.vector_retriever.retrieve(
            query=query,
            user=user,
            k=k,
        )

        print(f"""\n\nVector Results\n\n""")

        for result in results:
            print(f"{[result.metadata.get('source'),  result.metadata.get('similarity')]}")
        
        return results
    
    def _get_sql_results(
            self, *, query:str, user:User, k:int
    ) -> list[dict]:
        results = self.sql_retriever.retrieve(query=query, user=user)
        print(f"""\n\nSQL Results\n\n""")
        return results


    def run(self, query: str, user: User, k: int = 5, top_n: int = 4):
        if not self.vector_retriever:
            raise ValueError("Pipeline dependencies not initialised")

        vector_chunks = self._get_vector_results(query, user, k)
        sql_chunks = self._get_sql_results(query=query, user=user, k=k)

        output = {
            "vector": vector_chunks,
            "sql": sql_chunks
        }

        print(output)
        return output

        # routing =  self._route_query(query=query)
        # print(routing)
