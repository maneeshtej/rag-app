from src.database.guidance.guidance_retriever import GuidanceRetriever


class NL2SQLEngine:
    def __init__(self, llm, guidance_retriever):
        pass
        self.llm = llm
        self.guidance_retriever:GuidanceRetriever = guidance_retriever

    def _get_guidance_rules(self, *, query:str, soft_k:int = 5, hard_k:int = 7):
        schema_rules = self.guidance_retriever.retrieve(query=query, type="schema", soft_k=soft_k, hard_k=hard_k)

        generate_rules = self.guidance_retriever.retrieve(query=query, type="generate", soft_k=soft_k, hard_k=hard_k)

        entity_rules = self.guidance_retriever.retrieve(query=query, type="entity", soft_k=soft_k, hard_k=hard_k)

        return {
            "schema": schema_rules,
            "generate": generate_rules,
            "entity": entity_rules
        }


    def run(self, *, query:str) -> dict:
        guidance_rules:dict = self._get_guidance_rules(query=query)
        return guidance_rules