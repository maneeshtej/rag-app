import json
from urllib import response
from langchain_google_genai import ChatGoogleGenerativeAI
from src.database.entity.entity_retriever import EntityRetriever
from src.database.guidance.guidance_retriever import GuidanceRetriever
from src.models.guidance import GuidanceIngest

class NL2SQLEngine:
    def __init__(self, llm, guidance_retriever, entity_retriever):
        pass
        self.llm:ChatGoogleGenerativeAI = llm
        self.guidance_retriever:GuidanceRetriever = guidance_retriever
        self.entity_retriever:EntityRetriever = entity_retriever
        self.version = "0.0.8"
        self.logs = {}

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

        GENERAL
        - Use ONLY the information explicitly present in SCHEMA GUIDANCE.
        - Treat schema guidance as the single source of truth.
        - Do NOT use world knowledge or common-sense relationships.

        COLUMNS
        - Columns MUST be user-facing, semantic attributes.
        - Do NOT output relationship, linking, or foreign-key columns.
        - Examples of forbidden columns: *_id, handled_by, taught_by, assigned_to,
        class_teacher, teacher_id, subject_id.

        TABLES
        - Select ONE primary table per table entry.
        - Do NOT include columns from secondary tables unless the user explicitly asks
        for attributes of that table.

        RELATIONSHIPS
        - Do NOT invent or infer relationships between tables.
        - If a relationship is implied by the query but not represented in schema
        guidance, represent it ONLY as an entity filter.

        FILTERS
        - Filters MUST contain only:
        - entity_type
        - raw_value (exact surface form from user query)
        - Do NOT bind filters to columns.
        - Do NOT normalize, resolve, or transform entity values.

        AGGREGATES
        - Aggregates apply only to semantic columns of the selected table.
        - Aggregates imply intent = "aggregate".

        FAILURE
        - If the query requires a relationship or column not defined in schema guidance,
        return: {{ "skip": true }}

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
        guidance_rules = self.__get_guidance_rules(query=query, soft_k=soft_k, hard_k=hard_k)

        guidance_results = {
            "schema": [],
            "generate": [],
            "entity": []
        }

        schema_rules: list[GuidanceIngest] = guidance_rules.get("schema_rules") or []
        for rule in schema_rules:
            guidance_results["schema"].append({
                "name": rule.name,
                "similarity": rule.similarity
            })

        generate_rules: list[GuidanceIngest] = guidance_rules.get("generate_rules") or []
        for rule in generate_rules:
            guidance_results["generate"].append({
                "name": rule.name,
                "similarity": rule.similarity
            })

        entity_rules: list[GuidanceIngest] = guidance_rules.get("entity_rules") or []
        for rule in entity_rules:
            guidance_results["entity"].append({
                "name": rule.name,
                "similarity": rule.similarity
            })

        self.logs["rules"] = guidance_results


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

        return json.loads(response)
    
    def _resolve_entities(self, *, query_planning_object: dict) -> dict:
        """
        Resolve entity placeholders inside planner filters and attach confidence.
        Pipeline stops after this stage.
        """

        if query_planning_object.get("skip"):
            return query_planning_object

        HARD_MIN_SIMILARITY = 0.70
        SIMILARITY_MARGIN = 0.01

        resolved = dict(query_planning_object)
        filters = resolved.get("filters", [])

        for f in filters:
            results = self.entity_retriever.retrieve(
                queries={
                    "entity_type": f.get("entity_type"),
                    "surface_form": f.get("raw_value"),
                    "op": f.get("op"),
                },
                soft_k=3,
                hard_k=3,
            )

            # flatten resolved rows
            resolved_rows = []
            for r in results:
                resolved_rows.extend(r.get("resolved", []))

            f["resolved"] = resolved_rows

            # ---------- confidence logic ----------
            if not resolved_rows:
                f["confidence"] = "none"
                continue

            sorted_rows = sorted(
                resolved_rows, key=lambda r: r["similarity"], reverse=True
            )

            top = sorted_rows[0]

            # Absolute similarity gate
            if top["similarity"] < HARD_MIN_SIMILARITY:
                f["confidence"] = "low"
                continue

            entity_ids = {r["entity_id"] for r in sorted_rows}

            # Single-entity agreement
            if len(entity_ids) == 1:
                f["confidence"] = "high"
                continue

            # Relative separation
            if len(sorted_rows) == 1:
                f["confidence"] = "high"
                continue

            delta = sorted_rows[0]["similarity"] - sorted_rows[1]["similarity"]

            if delta >= SIMILARITY_MARGIN:
                f["confidence"] = "medium"
            else:
                f["confidence"] = "low"

        return resolved


    def run(self, *, query:str, **options) -> dict:
        soft_k = options.get("soft_k", 5)
        hard_k = options.get("hard_k", 7)

        query_planning_object = self._generate_query_planning(query=query, soft_k=soft_k, hard_k=hard_k)
        self.logs['query_planning_object'] = query_planning_object

        resolved_object = self._resolve_entities(query_planning_object=query_planning_object)
        self.logs['resolved_object'] = resolved_object

        return {
            "result": resolved_object,
            "logs":self.logs
        }

       