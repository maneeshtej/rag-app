import json
from asyncpg import NullValueNotAllowedError
from matplotlib import table
from sympy import use
from src.models.user import User
from src.database.guidance.guidance_retriever import GuidanceRetriever
from src.models.document import RuleChunk, SchemaChunk


class SQLRetriever:
    def __init__(self, *, guidance_retriever: GuidanceRetriever, llm, sql_store):
        self.guidance_retriever = guidance_retriever
        self.llm = llm
        self.sql_store = sql_store

    def _get_rules_and_schema(self, *, query:str, user:User, rule_k:int, schema_k:int) -> dict:
        rules: list[RuleChunk] = self.guidance_retriever.retrieve_query(
            query=query,
            user=user,
            type="rule",
            k=rule_k,
        )

        print("list of rules fetched:")
        for rule in rules:
            print(f"rule: {rule.name} similarity: {rule.similarity}")

        schema: list[SchemaChunk] = self.guidance_retriever.retrieve_schema(
            query=query,
            user=user,
            k=schema_k,
        )

        print("list of tables:")
        for table in schema:
            sim = (
                "related"
                if not table.similarity 
                else table.similarity
            )
            print(f"name: {table.name} similarity: {sim}")

        return {
        "rules": [rule.to_dict() for rule in rules],
        "schema": [chunk.to_dict() for chunk in schema],
    }

    def _normalize(self, *, query:str, rules:dict, schema:dict) -> dict:
        prompt = f"""
            You are helping to prepare a database query.

            Your job is NOT to write SQL.

            Your job is to perform STRUCTURAL NORMALIZATION only.

            You must:
            1. Identify the user’s high-level intent (list, exists, aggregate, or unknown).
            2. Identify concrete entities mentioned in the query (for example: departments,
            subjects, users, faculty).
            3. For each entity, specify which tables and columns should be searched to resolve possible matches.
            You MUST use ONLY columns explicitly listed under schema.entity_resolve_columns for that table.
            If a table does NOT define entity_resolve_columns, you MUST NOT use that table for entity resolution.
            If you dont find any suitable columns to search in do not mention the table in search targets.
            You MUST NOT use identifier columns such as id, *_id, timestamps, or metadata fields unless they are explicitly listed in entity_resolve_columns.
            4. Identify comparison expressions (>, <, >=, <=, =) and extract them
            without binding them to any column.
            5. Identify date or time expressions and normalize them into date ranges
            without binding them to any table or column.
            6. Split the query into independent sub-queries ONLY if the query explicitly
            contains multiple standalone requests.

            You are given:
            - The original user query
            - Retrieved rules (hints about what structures may exist)
            - Retrieved schema (available tables and columns)

            Rules are hints, NOT commands.
            Use ONLY the schema provided.
            Do NOT invent tables or columns.

            ----------------------------------
            USER QUERY:
            {query}
            ----------------------------------

            RETRIEVED RULE HINTS:
            {json.dumps(rules, indent=2, default=str)}
            ----------------------------------

            AVAILABLE SCHEMA:
            {json.dumps(schema, indent=2, default=str)}
            ----------------------------------

            OUTPUT FORMAT (JSON ONLY):

            {{
            "intent": {{
                "type": "list | exists | aggregate | unknown"
            }},

            "entities": [
                {{
                "entity_type": "department | subject | user | faculty | other",
                "raw_value": "<value exactly as in the query>",
                "search_targets": [
                    {{
                    "table": "<table_name>",
                    "columns": ["<column1>", "<column2>"]
                    }}
                ]
                }}
            ],

            "comparisons": [
                {{
                "operator": ">|<|>=|<=|=",
                "value": "<number or literal>",
                "raw_text": "<original phrase from the query>"
                }}
            ],

            "date_constraints": [
                {{
                "start_date": "<YYYY-MM-DD or null>",
                "end_date": "<YYYY-MM-DD or null>",
                "raw_text": "<original phrase from the query>"
                }}
            ],

            "splits": [
                {{
                "sub_query": "<standalone sub-query text>"
                }}
            ]
            }}

        STRICT OUTPUT RULES:
        - Output MUST be valid JSON.
        - Do NOT include comments, explanations, or annotations.
        - Do NOT include markdown or code fences.
        - Do NOT include text outside the JSON structure.
        - Do NOT infer joins, aggregations, or SQL logic.
        - Do NOT bind comparisons or dates to specific columns.
        - If a section does not apply, output an empty array.
        - Invalid JSON is a failure.
        """

        print(f"Token count normalize: {len(prompt) // 4}\n\n")

        response = self.llm.invoke(prompt)
        raw = response.content

        if not raw or not raw.strip():
            raise RuntimeError("LLM returned empty response")

        text = raw.strip()

        if text.startswith("```"):
            parts = text.split("```")
            if len(parts) < 2:
                raise RuntimeError("Malformed fenced JSON output")
            text = parts[1].strip()

            if text.lower().startswith("json"):
                text = text[4:].strip()

        return json.loads(text)
    
    def _resolve_entities(self, normalized: dict) -> dict:
        """
        Resolves entities in a normalized query structure.
        Returns a new normalized structure with resolved entities attached.
        """

        entities = normalized.get("entities", [])
        if not entities:
            raise ValueError("No entities found in normalized query")

        resolved_entities = []

        for entity in entities:
            raw_value = entity.get("raw_value")
            search_targets = entity.get("search_targets", [])

            # Skip entities without concrete value (e.g. result entity)
            if not raw_value or not search_targets:
                resolved_entities.append({
                    **entity,
                    "resolved": [],
                    "resolution_confidence": "none"
                })
                continue

            matches = []

            for target in search_targets:
                rows = self.sql_store.resolve_entity(
                    table=target["table"],
                    columns=target["columns"],
                    value=raw_value,
                    k=3
                )
                matches.extend(rows)

            resolved_entities.append({
                **entity,
                "resolved": matches,
                "resolution_confidence": (
                    "high" if len(matches) == 1
                    else "low" if len(matches) > 1
                    else "none"
                )
            })

        return {
            **normalized,
            "entities": resolved_entities
        }


    
    def _generate_sql_object(self, *, query:str, resolved_output:dict, schema:dict):
        prompt = f"""
        You are generating a SQL QUERY STRING for DEVELOPMENT PURPOSES ONLY.

        You are allowed to generate SQL text in this mode.

        Your job is to convert:
        - the original user query
        - the normalized and resolved output
        - the available table schemas

        into a VALID, EXECUTABLE SQL QUERY.

        ====================
        WHAT YOU MUST DO
        ====================

        1. Generate a SQL QUERY STRING (PostgreSQL dialect).
        2. Use ONLY the tables, columns, and joins provided in the schema.
        3. Do NOT invent tables, columns, joins, or filters.
        4. If the normalized output contains `splits`, generate ONE SQL QUERY PER sub_query.
        5. Select the MAXIMUM REASONABLE SET OF COLUMNS to produce rich results.
        - Prefer human-meaningful columns (names, titles, codes, timestamps).
        - Exclude pure identifiers unless required for joins or grouping.
        6. Use joins when they enrich the result (names, descriptions, codes).
        7. Respect entity resolution:
        - If `resolution_confidence` is high, apply filters using resolved entity IDs.
        - If `resolution_confidence` is none, DO NOT force filters.
        8. Use ONLY joins explicitly defined in the schema.
        9. ALL literal values MUST be parameterized using %s placeholders.
        - DO NOT inline values directly into SQL.

        ====================
        INPUTS
        ====================

        USER QUERY:
        {query}

        --------------------

        NORMALIZED & RESOLVED STRUCTURE:
        {json.dumps(resolved_output, indent=2, default=str)}

        --------------------

        AVAILABLE TABLE SCHEMAS:
        {json.dumps(schema, indent=2, default=str)}

        Each schema entry includes:
        - table name
        - column descriptions
        - join relationships
        - entity resolve columns

        These schemas are authoritative.

        ====================
        OUTPUT FORMAT
        ====================

        Output VALID JSON ONLY.

        If there are multiple sub_queries, output a JSON array.
        If there is only one query, output a single JSON object.

        OUTPUT FORMAT:

        {
        "sql": "<SQL QUERY STRING>",
        "params": [
            "<param1>",
            "<param2>"
        ]
        }

        ====================
        STRICT RULES
        ====================

        - Output JSON ONLY
        - No explanations
        - No comments
        - No markdown
        - SQL MUST be parameterized
        - No invented schema
        - Invalid JSON is a failure
        """

        
        print(f"Token count sql object: {len(prompt) // 4}\n\n")

        response = self.llm.invoke(prompt)
        raw = response.content

        if not raw or not raw.strip():
            raise RuntimeError("LLM returned empty response")

        text = raw.strip()

        if text.startswith("```"):
            parts = text.split("```")
            if len(parts) < 2:
                raise RuntimeError("Malformed fenced JSON output")
            text = parts[1].strip()

            if text.lower().startswith("json"):
                text = text[4:].strip()

        return json.loads(text)
        




    def retrieve(
        self,
        *,
        query: str,
        user: User,
        rule_k: int = 5,
        schema_k: int = 5,
    ) -> dict[str, list]:
        """Converts natural language to SQL
        
        Keyword arguments:

        - query -- user query 
        - user -- user object
        - rule_k -- number of rules
        - schema_k -- number of tables

        Return: returns rows from database
        """

        rules_and_schema = self._get_rules_and_schema(query=query, user=user, rule_k=rule_k, schema_k=schema_k)
        rules = rules_and_schema.get("rules")
        schema = rules_and_schema.get("schema")

        print("Running normalization...")
        normalized_result = self._normalize(query=query, rules=rules, schema=schema)
        print("Running resolution...")
        resolved_entities = self._resolve_entities(normalized=normalized_result)
        print("Running sql object generation...")
        sql_object = self._generate_sql_object(query=query, resolved_output=resolved_entities, schema=schema)

        print(normalized_result)
        print("\n\n")

        print(resolved_entities)
        print("\n\n")

        return sql_object


        

        

