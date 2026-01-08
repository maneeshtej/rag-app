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

    def _route_query(self, query: str) -> dict:
        prompt = f"""
            You are a query routing classifier.

            Your task is to decide how strongly a user query should use:
            1. SQL retrieval (structured, exact, database-style queries)
            2. Vector retrieval (semantic, descriptive, explanatory queries)

            IMPORTANT DATABASE CONTEXT:
            - The SQL database ONLY contains:
            faculty names,
            department names,
            subject names,
            and the relationships between them.
            - ALL other information (user details, explanations, descriptions,
            achievements, projects, narratives, definitions, and general knowledge)
            exists ONLY in the vector store.

            Return ONLY a valid JSON object.
            Do NOT explain.
            Do NOT add text.
            Do NOT use markdown.
            Do NOT repeat the query.

            STRICT OUTPUT FORMAT (exact keys, nothing extra):
            {{"sql_score":0.0,"vector_score":0.0}}

            SCORING RULES:
            - Give a HIGH sql_score ONLY if the query can be answered using:
            faculty, departments, subjects, or their relationships.
            - Give a HIGH vector_score if the query involves:
            explanations, descriptions, achievements, projects, definitions,
            general concepts, or any information NOT explicitly listed as SQL data.
            - Scores must be between 0.0 and 1.0.
            - Scores do NOT need to sum to 1.
            - It is valid for BOTH scores to be high.

            USER QUERY:
"{query}"


            """ 

        response = self.routing_llm.invoke(prompt)
        raw = response.content if hasattr(response, "content") else response

        # extract first JSON only (defensive)
        match = re.search(r"\{.*?\}", raw, re.DOTALL)
        if not match:
            # fail closed → SQL only
            return {
                "use_sql": True,
                "use_vector": False,
                "scores": {"sql_score": 1.0, "vector_score": 0.0},
            }

        scores = json.loads(match.group(0))

        sql_score = float(scores.get("sql_score", 0))
        vector_score = float(scores.get("vector_score", 0))

        return {
            "use_sql": sql_score >= 0.6,
            "use_vector": vector_score >= 0.6,
            "scores": scores,
        }


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
