import json
import re
from src.database.sql.prompts.retriever_prompt import build_generation_prompt, build_normalization_prompt
from src.models.guidance import GuidanceIngest
from src.models.user import User
from src.database.guidance.guidance_retriever import GuidanceRetriever


class SQLRetriever:
    def __init__(self, *, guidance_retriever, llm, sql_store, embedder, entity_retriver):
        self.guidance_retriever = guidance_retriever
        self.llm = llm
        self.sql_store = sql_store
        self.embedder = embedder
        self.entity_retriever = entity_retriver

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
            type="schema_guidance",
            soft_k=5

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
                   rules:list[str],  
                   schema:list[str]  
                   ) -> dict:
        prompt = build_normalization_prompt(query=query, rules=rules, schema=schema)

        print(f"Token count normalize: {len(prompt) // 4}\n\n")

        print(prompt)

        response = self.llm.invoke(prompt)
        raw = response.content

        print(f"Raw output: \n\n${raw}\n\n")

        if not raw or not raw.strip():
            raise RuntimeError("LLM returned empty response")

        text = (raw or "").strip()

        # 1. Try direct JSON (best case)
        if text.startswith("{") and text.endswith("}"):
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass

        # 2. Handle fenced blocks ```json ... ```
        m = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text, re.IGNORECASE)
        if m:
            try:
                return json.loads(m.group(1))
            except json.JSONDecodeError:
                pass

        # 3. Last resort: extract first JSON object anywhere
        m = re.search(r"\{[\s\S]*?\}", text)
        if m:
            try:
                return json.loads(m.group())
            except json.JSONDecodeError:
                pass

        # 4. Hard fail → deterministic output
        return { "skip": True }


    
    def _resolve_entities(self, *, normalized: dict) -> dict:
        if normalized.get("skip") is True:
            return normalized

        new_queries = []

        for q in normalized.get("queries", []):
            entities = q.get("entities", [])

            queries = []
            index_map = []

            for entity in entities:
                et = entity.get("entity_type")
                rv = entity.get("raw_value")

                if not et or not rv:
                    index_map.append(None)
                    continue

                queries.append({
                    "surface_form": rv,
                    "entity_type": et,
                })
                index_map.append(len(queries) - 1)

            resolved_queries = self.entity_retriever.retrieve(
                queries,
                soft_k=1,
                hard_k=3,
                threshold=0.7,
            ) if queries else []

            resolved_entities = []

            for entity, map_idx in zip(entities, index_map):
                if map_idx is None:
                    resolved_entities.append({
                        **entity,
                        "resolved": [],
                        "resolution_confidence": "none",
                    })
                    continue

                resolved = resolved_queries[map_idx].get("resolved", [])

                resolved_entities.append({
                    **entity,
                    "resolved": resolved,
                    "resolution_confidence": (
                        "high" if len(resolved) == 1
                        else "low" if len(resolved) > 1
                        else "none"
                    )
                })

            new_queries.append({
                **q,
                "entities": resolved_entities,
            })

        return {
            **normalized,
            "queries": new_queries,
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
                             resolved_output:dict, 
                             schema:list[str],
                             generate_rules:list[str]
                             ):
        prompt = build_generation_prompt(resolved_output=resolved_output, schema=schema, generate_rules=generate_rules)

        
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
        minimal_schema = [row.to_prompt_block() for row in schema]

        print("Running normalization...")
        normalized_result = self._normalize(
            query=query,
            rules=minimal_rules,
            schema=minimal_schema,
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

        final_results = []

        for q in resolved_output.get("queries", []):
            generate_rules:list[GuidanceIngest] = self._get_generate_rules(query=q['text'])
            minimal_generate_rules = [rules.to_prompt_block() for rules in generate_rules]

            sql_objects = self._generate_sql_object(
                resolved_output=q,
                schema=minimal_schema,
                generate_rules=minimal_generate_rules
            )

            if not sql_objects:
                continue

            print(sql_objects)

            rows = self._run_sql_objects(sql_objects=sql_objects)

            final_results.append(rows)

        print(f"\n\n\nFinal results: {final_results}\n\n\n")


        # generate_rules:list[GuidanceIngest] = self._get_generate_rules(query=query)

        # minimal_generate_rules = [rule.to_prompt_block()
        #                           for rule in generate_rules]

        # print("Running SQL object generation...")
        # sql_objects_list = self._generate_sql_object(
        #     query=query,
        #     resolved_output=resolved_output,
        #     schema=minimal_schema,
        #     generate_rules=minimal_generate_rules
        # )

        # print(sql_objects_list)
        # print("\n")

        # print("Running SQL rows...")
        # sql_rows = self._run_sql_objects(sql_objects=sql_objects_list)
        # print(sql_rows)

        # return sql_rows
    
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




        

        

