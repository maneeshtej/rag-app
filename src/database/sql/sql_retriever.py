import json
import re
from src.models.user import User
from src.database.guidance.guidance_retriever import GuidanceRetriever
from src.models.document import RuleChunk, SchemaChunk


class SQLRetriever:
    def __init__(self, *, guidance_retriever: GuidanceRetriever, llm, sql_store, embedder):
        self.guidance_retriever = guidance_retriever
        self.llm = llm
        self.sql_store = sql_store
        self.embedder = embedder

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

        result =  {
        "rules":rules,
        "schema": schema,
        }

        # print(result)

        return result

    def _normalize(self, *, query:str, rules:list[dict], schema:list[dict]) -> dict:
        prompt = f"""
            You are helping to prepare a database query.

            Your job is NOT to write SQL.

            Your job is to perform STRUCTURAL NORMALIZATION only.

            Before doing anything else, you MUST decide whether the user query
            is meaningfully answerable using the provided database schema.

            - If the query is informational, conceptual, explanatory, or refers
            to data NOT present in the schema, output EXACTLY:
            {{ "skip": true }}

            - If the query CAN be answered using the schema, continue with
            structural normalization and output {{ "skip": false, ... }}.

            You must perform the following ONLY if skip is false:

            1. Identify the user’s high-level intent
            (list, exists, aggregate, or unknown).

            2. Identify concrete entities mentioned in the query
            (for example: departments, subjects, users, faculty).

            3. Identify which database tables are relevant to answering the query.
            - Output ONLY table names.
            - Do NOT output column names.
            - Do NOT infer joins, filters, or conditions.
            - If no tables are clearly relevant, leave the table list empty.


            4. Identify comparison expressions (>, <, >=, <=, =)
            and extract them WITHOUT binding them to any column.

            5. Identify date or time expressions and normalize them into date ranges
            WITHOUT binding them to any table or column.

            6. Identify whether the query contains multiple independent,
            standalone requests.
            - Split ONLY if each sub-query can stand alone and be answered independently.
            - If splitting is not clearly justified, do NOT split.

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

            If the query is NOT suitable for database processing, output EXACTLY:

            {{
            "skip": true
            }}

            Otherwise, output EXACTLY:

            {{
            "skip": false,

            "intent": {{
                "type": "list | exists | aggregate | unknown"
            }},

            "tables": ["subjects | faculty"],

            "entities": [
                {{
                    "entity_type": "department | subject | faculty | other",
                    "raw_value": "<value exactly as in the query>"
                }}
            ]


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
            - Output MUST be either {{ "skip": true }} OR the full normalized object.
            - Do NOT mix skip with other fields.
            - Do NOT include comments, explanations, or annotations.
            - Do NOT include markdown or code fences.
            - Do NOT infer joins, aggregations, or SQL logic.
            - Do NOT bind comparisons or dates to specific columns.
            - If a section does not apply, output an empty array.
            - Invalid JSON is a failure.

        """

        print(f"Token count normalize: {len(prompt) // 4}\n\n")

        print(prompt)

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
    
    def _resolve_single_entity(
        self,
        *,
        entity_type: str,
        query: str,
        k: int = 3,
        max_distance: float = 0.8,
    ) -> list[dict]:
        """
        Resolve entities using vector search over entity_embeddings
        and return canonical rows from source tables.
        """

        query_vec = self.embedder.embed_query(query)

        if entity_type == "faculty":
            join_sql = "JOIN faculty f ON f.id = e.entity_id"
            select_cols = """
                e.entity_id,
                f.name,
                f.designation,
                f.email,
                e.surface_form,
                e.embedding <-> %s::vector AS distance
            """
        elif entity_type == "subject":
            join_sql = "JOIN subjects s ON s.id = e.entity_id"
            select_cols = """
                e.entity_id,
                s.name,
                e.surface_form,
                e.embedding <-> %s::vector AS distance
            """
        else:
            return []

        sql = f"""
            SELECT
                x.*
            FROM (
                SELECT DISTINCT ON (e.entity_id)
                    {select_cols}
                FROM entity_embeddings e
                {join_sql}
                WHERE e.entity_type = %s
                ORDER BY e.entity_id, distance
            ) x
            ORDER BY x.distance
        """

        rows = self.sql_store.execute_read(
            sql=sql,
            params=(query_vec, entity_type),
            limit=k
        )

        # hard safety gate — reject garbage matches
        return [r for r in rows if r["distance"] is not None and r["distance"] < max_distance]
    
    def _resolve_entities(self, *, normalized: dict) -> dict:
        if normalized.get("skip") is True:
            return {**normalized, "entities": []}

        resolved_output = []

        for entity in normalized.get("entities", []):
            entity_type = entity.get("entity_type")
            raw_value = entity.get("raw_value")

            if not entity_type or not raw_value:
                resolved_output.append({
                    **entity,
                    "resolved": [],
                    "resolution_confidence": "none",
                })
                continue

            matches = self._resolve_single_entity(
                entity_type=entity_type,
                query=raw_value,
            )

            resolved_output.append({
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
            "entities": resolved_output,
        }





    
    def _generate_sql_object(self, *, query:str, resolved_output:dict, schema:dict):
        prompt = f"""
        You are generating SQL QUERY STRINGS for DEVELOPMENT PURPOSES ONLY.

        You are allowed to generate SQL text in this mode.

        Your job is to convert:
        - the original user query
        - the normalized and resolved output
        - the available table schemas

        into VALID, EXECUTABLE SQL QUERY STRINGS.

        Before doing anything else, you MUST check the normalized output:

        - If the normalized output contains:
        {{ "skip": true }}
        then you MUST return EXACTLY:
        []

        - If skip is false, proceed with SQL generation.

        ====================
        WHAT YOU MUST DO
        ====================

        1. Generate SQL QUERY STRINGS (PostgreSQL dialect).
        2. Use ONLY the tables, columns, and joins provided in the schema.
        3. Do NOT invent tables, columns, joins, or filters.
        4. If the normalized output contains `splits`,
        generate ONE SQL QUERY OBJECT PER sub_query.
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
        10. Generate SELECT queries ONLY.

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
        - table purpose and relationsips

        These schemas are authoritative.

        ====================
        OUTPUT FORMAT
        ====================

        You MUST output a JSON ARRAY.

        - The FIRST character of the output MUST be '['
        - The LAST character of the output MUST be ']'
        - Even if there is only ONE SQL query, wrap it in an array.
        - If no SQL should be generated, output EXACTLY: []

        OUTPUT FORMAT (EXACT):

        [
        {{ 
        "sql": "<SQL QUERY STRING>",
        "params": [
            "<param1>",
            "<param2>"
        ]
        }}
        ]

        ====================
        STRICT RULES
        ====================

        - You MUST output VALID JSON ONLY.
        - The output MUST be a JSON ARRAY.
        - The JSON ARRAY MUST be the ONLY content in the output.
        - The output MUST start with '[' and end with ']'.
        - Do NOT include any text before the JSON array.
        - Do NOT include any text after the JSON array.
        - Do NOT include explanations, reasoning, comments, annotations, or summaries.
        - Do NOT include markdown, code fences, or formatting of any kind.
        - If no SQL should be generated, output an EMPTY JSON ARRAY: [].
        - SQL MUST be parameterized using %s placeholders.
        - Do NOT invent tables, columns, joins, or filters.
        - Generate SELECT statements ONLY.

        ====================
        SELF-CHECK (MANDATORY)
        ====================

        Before finalizing your output:
        - Verify that the output is ONLY a JSON array.
        - If you have included ANY non-JSON text,
        DELETE IT and output ONLY the JSON array.

        Any output that violates these rules is INVALID.
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

        if not text:
            return []

        match = re.search(r"\[\s*\{.*?\}\s*\]", text, re.DOTALL)
        if not match:
            print("⚠️ No JSON array found in SQL LLM output")
            return []

        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError:
            print("⚠️ SQL generation returned invalid JSON. Raw output:")
            print(match.group(0))
            return []

        # Enforce list contract
        if not isinstance(parsed, list):
            print("⚠️ SQL generation did not return a list.")
            return []

        return parsed


    
    def _run_sql_objects(
    self,
    *,
    sql_objects: list[dict],
    limit: int = 100,
    ) -> list[dict]:
        results: list[dict] = []

        for obj in sql_objects:
            sql = obj.get("sql")
            params = obj.get("params", [])

            if not sql:
                continue

            rows = self.sql_store.execute_read(
                sql=sql,
                params=tuple(params),
                limit=limit,
            )

            results.append({
                "rows": rows
            })

        return results

    def retrieve(
    self,
    *,
    query: str,
    user: User,
    rule_k: int = 5,
    schema_k: int = 5,
    ) -> dict[str, list]:
        """
        Converts natural language to SQL objects.

        Returns:
        - [] if query is not suitable for SQL
        - list of SQL objects otherwise
        """
        rules_and_schema = self._get_rules_and_schema(
            query=query,
            user=user,
            rule_k=rule_k,
            schema_k=schema_k,
        )
        rules:list[RuleChunk] = rules_and_schema.get("rules", [])
        schema:list[SchemaChunk] = rules_and_schema.get("schema", [])

        minimal_rules = [rule.to_minimal_dict() for rule in rules]
        minmal_schema = [row.to_minimal_dict() for row in schema]

        print("Running normalization...")
        normalized_result = self._normalize(
            query=query,
            rules=minimal_rules,
            schema=minmal_schema,
        )

        print(normalized_result)
        print("\n")

        if normalized_result.get("skip") is True:
            print("Skipping SQL generation (not DB-related query).")
            return []

        print("Running resolution...")
        resolved_output = self._resolve_entities(
            normalized=normalized_result
        )


        print(resolved_output)
        print("\n")

        print("Running SQL object generation...")
        sql_objects_list = self._generate_sql_object(
            query=query,
            resolved_output=resolved_output,
            schema=schema,
        )

        print(sql_objects_list)
        print("\n")

        print("Running SQL rows...")
        sql_rows = self._run_sql_objects(sql_objects=sql_objects_list)
        print(sql_rows)

        return sql_rows
    
    def get_row(
        self,
        *,
        table: str,
        where: dict,
    ) -> dict | None:
        """
        Fetch a single row from a table using equality filters.
        """
        if not where:
            raise ValueError("where cannot be empty")

        conditions = " AND ".join(f"{k} = %s" for k in where)
        sql = f"SELECT * FROM {table} WHERE {conditions} LIMIT 1"

        rows = self.sql_store.execute_read(
            sql=sql,
            params=tuple(where.values()),
            limit=1,
        )

        return rows[0] if rows else None




        

        

