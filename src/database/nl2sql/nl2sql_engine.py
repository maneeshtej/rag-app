import json
from urllib import response
from langchain_google_genai import ChatGoogleGenerativeAI
from src.database.guidance.guidance_retriever import GuidanceRetriever
from src.models.guidance import GuidanceIngest

class NL2SQLEngine:
    def __init__(self, llm, guidance_retriever):
        pass
        self.llm:ChatGoogleGenerativeAI = llm
        self.guidance_retriever:GuidanceRetriever = guidance_retriever
        self.version = "1.1.0"

    def __get_guidance_rules(self, *, query:str, soft_k:int = 5, hard_k:int = 7) -> dict:
        """
        query (str), soft_k (int), hard_k (int)\n
        Returns: {"schema": [GuidanceIngest], "generate": [GuidanceIngest], "entity": [GuidanceIngest]}
        """

        
        schema_rules = self.guidance_retriever.retrieve(query=query, type="schema", soft_k=soft_k, hard_k=hard_k)

        generate_rules = self.guidance_retriever.retrieve(query=query, type="generate", soft_k=soft_k, hard_k=hard_k)

        entity_rules = self.guidance_retriever.retrieve(query=query, type="entity", soft_k=soft_k, hard_k=hard_k)

        return {
            "schema_rules": schema_rules,
            "generate_rules": generate_rules,
            "entity_rules": entity_rules
        }
    
    def __generate_llm_prompt(self, *, query, schema_rules, generate_rules, entity_rules) -> str:
        """
        Build the NL2SQL planner prompt from query and guidance rules.
        """
        return f"""
        You are an NL2SQL QUERY PLANNER.

        You do NOT write SQL.
        You do NOT resolve IDs.
        You do NOT decide joins.

        Your job is to output a SINGLE JSON object describing a logical query plan.

        ====================
        SCHEMA GUIDANCE
        ====================
        {schema_rules}

        ====================
        GENERATION GUIDANCE
        ====================
        {generate_rules}

        ====================
        ENTITY GUIDANCE
        ====================
        {entity_rules}

        ====================
        USER QUERY
        ====================
        {query}

        ====================
        OUTPUT FORMAT (STRICT)
        ====================

        If not answerable:
        {{ "skip": true }}

        Otherwise output exactly:

        {{
        "skip": false,
        "intent": "list | exists | aggregate | unknown",
        "tables": [
            {{
            "name": "table_name",
            "columns": ["semantic_column"],
            "aggregates": [
                {{
                "type": "count | sum | avg | min | max",
                "column": "semantic_column"
                }}
            ] | null
            }}
        ],
        "filters": [
            {{
            "op": "= | != | > | >= | < | <=",
            "entity_type": "entity_type",
            "raw_value": "exact text from query"
            }}
        ],
        "limit": null
        }}

        ====================
        RULES
        ====================
        - Use only provided schema
        - Do not invent joins, IDs, or columns
        - Filters must contain only entity placeholders
        - Aggregates imply intent = "aggregate"
        - If unsure, return skip=true
        """
    
    
    def _generate_query_planning(self, *, query: str, soft_k: int, hard_k: int) -> dict:
        """
        Args:
            query (str), soft_k (int), hard_k (int)
        Returns:
            dict: {
                "skip": bool,
                "intent": str,
                "tables": [
                    {
                        "name": str,
                        "columns": list[str],
                        "aggregates": list[dict] | None
                    }
                ],
                "filters": [
                    {
                        "op": str,
                        "entity_type": str,
                        "raw_value": str
                    }
                ],
                "limit": int | None
            }
        """
        self.current_step = 10
        guidance_rules = self.__get_guidance_rules(query=query, soft_k=soft_k, hard_k=hard_k)

        schema_rules = guidance_rules.get("schema") or []
        generate_rules = guidance_rules.get("generate") or []
        entity_rules = guidance_rules.get("entity") or []

        minimal_schema_rules = [r.to_prompt_block() for r in schema_rules]
        minimal_generate_rules = [r.to_prompt_block() for r in generate_rules]
        minimal_entity_rules = [r.to_prompt_block() for r in entity_rules]

        prompt = self.__generate_llm_prompt(
            query=query,
            schema_rules=minimal_schema_rules,
            generate_rules=minimal_generate_rules,
            entity_rules=minimal_entity_rules,
        )

        raw_output = self.llm.invoke(input=prompt)
        response = raw_output.content

        self.outputs[10] = json.loads(response)

        return json.loads(response)



    def run(self, *, query:str, **options) -> dict:
        soft_k = options.get("soft_k", 5)
        hard_k = options.get("hard_k", 7)

        query_planning_object = self._generate_query_planning(query=query, soft_k=soft_k, hard_k=hard_k)

        return query_planning_object

       