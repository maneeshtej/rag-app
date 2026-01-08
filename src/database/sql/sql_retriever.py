import json
import re
from src.models.guidance import GuidanceIngest
from src.models.user import User
from src.database.guidance.guidance_retriever import GuidanceRetriever


class SQLRetriever:
    def __init__(self, *, guidance_retriever:GuidanceRetriever, llm, sql_store, embedder):
        self.guidance_retriever = guidance_retriever
        self.llm = llm
        self.sql_store = sql_store
        self.embedder = embedder

    def _get_rules_and_schema(
        self,
        *,
        query: str,
        user: User,
        rule_k: int,
        schema_k: int,
    ) -> dict:
        rules: list[GuidanceIngest] = self.guidance_retriever.retrieve(
            query=query,
            type="realisation_rules"
        )

        print("list of rules fetched:")
        for rule in rules:
            print(
                f"rule: {rule.name} "
                f"distance: {getattr(rule, 'distance', None)}"
            )

        schema: list[GuidanceIngest] = self.guidance_retriever.retrieve(
            query=query,
            type="schema_guidance"
        )

        print("list of schema fetched:")
        for table in schema:
            print(
                f"name: {table.name} "
                f"distance: {getattr(table, 'distance', None)}"
            )

        return {
            "rules": rules,
            "schema": schema,
        }


    def _normalize(self, 
                   *, 
                   query:str, 
                   rules:list[str],  # GuidanceIngest object to str
                   schema:list[str]  # GuidanceIngest object to str
                   ) -> dict:
        prompt = f"""You are performing STRUCTURAL NORMALIZATION for database querying.
        You must NOT write SQL.

        First, decide if the query can be answered using the provided schema.

        - If NOT answerable, output exactly:
        {{ "skip": true }}

        - Otherwise, output {{ "skip": false, ... }} and continue.

        ====================
        TASKS (ONLY IF skip=false)
        ====================

        1. Identify the high-level intent:
        - list | exists | aggregate | unknown

        2. Extract entities explicitly mentioned in the query.
        For each:
        - entity_type: department | subject | faculty | event | other
        - raw_value: exact surface form from the query

        3. List relevant database tables (table names only).
        This list is advisory.

        4. Extract comparison expressions (>, <, >=, <=, =), if any.

        5. Extract date/time expressions and normalize to date ranges.

        6. Determine if the query contains multiple independent sub-queries.
        Split ONLY if each can stand alone.

        RULE USAGE INSTRUCTION:
        - The retrieved RULE HINTS describe what entities and structures to extract.
        - You MUST follow these rules when identifying entities and intent.
        - Rules guide extraction, but MUST NOT cause you to invent tables or columns.

        ====================
        INPUTS
        ====================

        USER QUERY:
        {query}

        RULE HINTS:
        {rules}

        AVAILABLE SCHEMA:
        {schema}

        ====================
        OUTPUT FORMAT (JSON ONLY)
        ====================

        {{ 
        "skip": true 
        }}

        OR

        {{
        "skip": false,
        "intent": {{ "type": "list | exists | aggregate | unknown" }},
        "tables": [],
        "entities": [],
        "comparisons": [],
        "date_constraints": [],
        "splits": []
        }}

        ====================
        STRICT RULES
        ====================

        - Output VALID JSON only.
        - Do NOT write SQL.
        - Do NOT infer joins, columns, or filters.
        - If a section does not apply, return an empty array.
        HARD RULE:
        If AVAILABLE SCHEMA is empty or missing,
        you MUST output exactly:
        {{ "skip": true }}
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
        return [r for r in rows if r["distance"] is not None]

    
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
    
    def _get_generate_rules(self, *, query:str) -> list[GuidanceIngest]:
        rules = self.guidance_retriever.retrieve(
            query=query,
            type="generate_rules"
        )

        print("\n\nFetched rules:\n\n")
        for rule in rules:
            print(f"{rule.name} {rule.similarity}")

        return rules

    def _generate_sql_object(self, 
                             *, 
                             query:str, 
                             resolved_output:dict, 
                             schema:list[str],
                             generate_rules:list[str]
                             ):
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
        5. Select columns required to answer the query.
        6. Respect entity resolution:
        - If `resolution_confidence` is high, apply filters using resolved entity IDs.
        - If `resolution_confidence` is none, DO NOT force filters.
        7. Use ONLY joins explicitly defined in the schema.
        8. ALL literal values MUST be parameterized using %s placeholders.
        - DO NOT inline values directly into SQL.
        9. Generate SELECT queries ONLY.

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
        {schema}

        Each schema entry includes:
        - table name
        - column descriptions
        - join relationships
        - table purpose and relationsips

        These schemas are authoritative.

        ====================
        GENERATION RULES
        ====================

        The following rules control WHAT columns should be selected
        and how rich the result should be.

        These rules:
        - Affect column selection only
        - MUST NOT introduce new tables, joins, or filters
        - MUST NOT override the schema

        {generate_rules}


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
        rules:list[GuidanceIngest] = rules_and_schema.get("rules", [])
        schema:list[GuidanceIngest] = rules_and_schema.get("schema", [])

        minimal_rules = [rule.to_prompt_block() for rule in rules]
        minmal_schema = [row.to_prompt_block() for row in schema]

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

        generate_rules:list[GuidanceIngest] = self._get_generate_rules(query=query)

        minimal_generate_rules = [rule.to_prompt_block()
                                  for rule in generate_rules]

        print("Running SQL object generation...")
        sql_objects_list = self._generate_sql_object(
            query=query,
            resolved_output=resolved_output,
            schema=minmal_schema,
            generate_rules=minimal_generate_rules
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




        

        

