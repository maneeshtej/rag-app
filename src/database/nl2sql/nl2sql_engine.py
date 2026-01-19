import json
from urllib import response
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from pyparsing import col
from src.bootstrap.bootstrap import create_entity_ingestor, create_entity_retriever, create_entity_store, create_guidance_ingestor, create_guidance_retriever, create_guidance_store, create_sql_store
from src.database.column.column_retriever import ColumnRetriever
from src.database.column.column_store import ColumnStore
from src.database.db import get_dev_connection
from src.database.dependencies import create_embedder
from src.database.entity.entity_retriever import EntityRetriever
from src.database.guidance.guidance_retriever import GuidanceRetriever
from src.database.llm import create_google_llm, create_groq_llm
from src.database.sql.sql_retriever import SQLRetriever
from src.database.sql.sql_store import SQLStore
from src.models.guidance import GuidanceIngest
from src.schema.joins.joins import JOIN_GRAPH

class NL2SQLEngine:
    def __init__(self, llm, guidance_retriever, entity_retriever, sql_store, column_retriever):
        pass
        self.llm:ChatGoogleGenerativeAI = llm
        self.guidance_retriever:GuidanceRetriever = guidance_retriever
        self.entity_retriever:EntityRetriever = entity_retriever
        self.sql_store:SQLStore = sql_store
        self.column_retriever:ColumnRetriever = column_retriever
        self.version = "0.0.13"
        self.logs = {}

    def __get_guidance_rules(self, *, query:str, soft_k:int = 5, hard_k:int = 7) -> dict:
        """
        query (str), soft_k (int), hard_k (int)\n
        Returns: {"schema": [GuidanceIngest], "generate": [GuidanceIngest], "entity": [GuidanceIngest]}
        """

        
        schema_rules = self.guidance_retriever.retrieve(query=query, type="schema", soft_k=soft_k, hard_k=hard_k)


        entity_rules = self.guidance_retriever.retrieve(query=query, type="entity", soft_k=soft_k, hard_k=hard_k)

        return {
            "schema_rules": schema_rules,
            "entity_rules": entity_rules
        }
    
    def __generate_llm_prompt(self, *, query, schema_rules, entity_rules) -> str:
        """
        Build the NL2SQL planner prompt from query and guidance rules.
        """
        return f"""
        You are an NL2SQL QUERY PLANNER.

        You do NOT write SQL.
        You do NOT resolve IDs.
        You do NOT decide join paths.

        You output a SINGLE JSON object describing a logical query plan.
        This plan will be compiled deterministically into SQL by downstream code.

        RESPONSIBILITY BOUNDARY:
        Downstream logic will compute joins, validate foreign keys, execute SQL,
        and post-process result columns. You must not perform those steps.

        SCHEMA GUIDANCE:
        {schema_rules}

        ENTITY GUIDANCE:
        {entity_rules}

        USER QUERY:
        {query}

        ====================
        CRITICAL ENTITY RULE (HARD CONSTRAINT)
        ====================

        Entity types MUST be taken ONLY from ENTITY GUIDANCE.

        - entity_type values MUST exactly match entity_rules (e.g. "teacher", "subject").
        - entity_type MUST NEVER be derived from:
        - table names
        - aliases
        - pluralization or singularization
        - schema object names

        Table names (e.g. "teachers", "subjects") represent STORAGE.
        Entity types (e.g. "teacher", "subject") represent SEMANTIC CONCEPTS.
        These are separate and MUST NOT be conflated.

        If an entity is extracted:
        - Use the entity_type defined in entity_rules.
        - Do NOT invent new entity types.
        - Do NOT reuse table names as entity types.


        OUTPUT FORMAT (STRICT):

        If the query cannot be represented:
        {{ "skip": true }}

        Otherwise output exactly:

        {{
        "skip": false,
        "intent": "list | exists | aggregate | unknown",

        "base_table": "table_name",

        "tables": ["table_name"],

        "aliases": {{
            "table_name": "t"
        }},

        "filters": [
            {{
                "entity_type": "teacher | subject | null",
                "column_hint": "semantic_column_name | null",
                "op": "= | != | > | >= | < | <=",
                "raw_value": "exact text from query"
            }}
        ]

        "join_intent": [
            ["table_a", "table_b"]
        ],

        "aggregates": [
            {{
            "type": "count | sum | avg | min | max",
            "column": "alias.semantic_column"
            }}
        ] | null,

        "limit": null
        }}

        HARD RULES (NON-NEGOTIABLE):

        GENERAL:
        - Treat all rules as hard constraints.
        - Output valid JSON only.
        - No explanations or extra fields.

        ALIASES:
        - Every table MUST have an alias.
        - Aliases MUST be short and consistent.
        - Use aliases in all column references.

        FILTERS:
        - Filters MUST reference resolved columns using aliases.
        - Do NOT use entity-only filters.
        - raw_value must match user query text exactly.

        COLUMNS:
        - Columns must be semantic, user-facing attributes.
        - Do NOT output *_id or relational columns.

        JOIN INTENT:
        - Express relationships only as table-to-table intent.
        - Do NOT infer join paths or conditions.

        AGGREGATES:
        - Aggregates imply intent = "aggregate".
        - Aggregates apply only to semantic columns.

        FAILURE:
        Return {{ "skip": true }} only if the query cannot be represented
        using the provided schema guidance.

        """

    def _extract_json(self, *, response: str) -> str:
        if not response or not response.strip():
            raise RuntimeError("Empty LLM response")

        # remove fenced code blocks markers
        cleaned = response.replace("```json", "").replace("```", "").strip()

        # extract first JSON object
        match = re.search(r"\{.*\}", cleaned, re.S)
        if not match:
            raise RuntimeError(f"No JSON object found in LLM output: {repr(response)}")

        return match.group()

    
    
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
            "entity": []
        }

        schema_rules: list[GuidanceIngest] = guidance_rules.get("schema_rules") or []
        for rule in schema_rules:
            guidance_results["schema"].append({
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
        minimal_entity_rules = [r.to_prompt_block() for r in entity_rules]

        prompt = self.__generate_llm_prompt(
            query=query,
            schema_rules=minimal_schema_rules,
            entity_rules=minimal_entity_rules,
        )

        raw_output = self.llm.invoke(input=prompt)
        raw = raw_output.content
        json_str = self._extract_json(response=raw)
        query_planning_object = json.loads(json_str)

        return query_planning_object
    
    def _resolve_entities(self, *, query_planning_object: dict) -> tuple[list, dict]:
        """
        Resolve entity placeholders inside planner filters and attach confidence.

        Returns:
        - hydrated_rows: list of hydrated entity rows (flattened)
        - updated_query_planning_object
        """

        if query_planning_object.get("skip"):
            return [], query_planning_object

        HARD_MIN_SIMILARITY = 0.70
        SIMILARITY_MARGIN = 0.01

        resolved = dict(query_planning_object)
        filters = resolved.get("filters", [])

        all_hydrated_rows = []

        for idx, f in enumerate(filters):
            col = f.get("column")
            raw_value = f.get("raw_value")
            entity_type = f.get("entity_type")

            # ---------- HARD VALIDATION (FAIL LOUDLY) ----------
            if not col or "." not in col:
                raise ValueError(
                    f"[ENTITY RESOLUTION] Missing or invalid column in filter[{idx}]: {f}"
                )

            if not entity_type:
                raise ValueError(
                    f"[ENTITY RESOLUTION] Missing entity_type in filter[{idx}]: {f}"
                )

            if not raw_value:
                raise ValueError(
                    f"[ENTITY RESOLUTION] Missing raw_value in filter[{idx}]: {f}"
                )

            # ---------- ENTITY RETRIEVAL ----------
            results = self.entity_retriever.retrieve(
                queries={
                    "entity_type": entity_type,
                    "surface_form": raw_value,
                    "op": f.get("op"),
                },
                soft_k=3,
                hard_k=5,
            )

            resolved_rows = []
            for r in results:
                resolved_rows.extend(r.get("resolved", []))

            # resolved ALWAYS lives on the filter
            f["resolved"] = resolved_rows

            # ---------- HYDRATION ----------
            hydrated = []
            for r in resolved_rows:
                table = r["source_table"]
                entity_id = r["entity_id"]

                rows = self.sql_store.execute_read(
                    sql=f"SELECT * FROM {table} WHERE id=%s",
                    params=(entity_id,),
                )

                # 0 DB rows is VALID — do NOT fail
                if rows:
                    row = {
                        **rows[0],
                        "_entity_table": table,
                        "_similarity": r["similarity"],
                    }
                    hydrated.append(row)
                    all_hydrated_rows.append(row)

            f["hydrated"] = hydrated

            # ---------- CONFIDENCE ----------
            if not resolved_rows:
                f["confidence"] = "none"
                continue

            sorted_rows = sorted(
                resolved_rows, key=lambda r: r["similarity"], reverse=True
            )

            top = sorted_rows[0]

            if top["similarity"] < HARD_MIN_SIMILARITY:
                f["confidence"] = "low"
                continue

            entity_ids = {r["entity_id"] for r in sorted_rows}

            if len(entity_ids) == 1:
                f["confidence"] = "high"
                continue

            if len(sorted_rows) == 1:
                f["confidence"] = "high"
                continue

            delta = sorted_rows[0]["similarity"] - sorted_rows[1]["similarity"]

            f["confidence"] = "medium" if delta >= SIMILARITY_MARGIN else "low"

        resolved["continue"] = all(
            f.get("confidence") == "high"
            for f in resolved.get("filters", [])
        )

        return all_hydrated_rows, resolved




    def _resolve_columns(self, *, resolved_object: dict) -> tuple[dict, dict]:
        """
        Resolve semantic column hints inside filters to physical column names.
        Mutates the object in-place.
        Returns:
        - updated resolved_object
        - resolved_columns_map {old: new}
        """

        if resolved_object.get("skip"):
            return resolved_object, {}

        resolved_columns_map = {}

        aliases = resolved_object.get("aliases", {})
        filters = resolved_object.get("filters", [])

        # alias -> table
        alias_to_table = {v: k for k, v in aliases.items()}

        for f in filters:
            column_hint = f.get("column_hint")

            # nothing to resolve
            if not column_hint:
                continue

            resolved = None
            resolved_from = None

            # try resolving against ALL tables deterministically
            for table_name, alias in aliases.items():
                results = self.column_retriever.retrieve(
                    semantic_column=column_hint,
                    table_name=table_name,
                    k=3,
                )
                if results:
                    resolved = results[0]["column_name"]
                    resolved_from = table_name
                    break

            if not resolved:
                raise ValueError(
                    f"Could not resolve column for hint '{column_hint}'"
                )

            alias = aliases[resolved_from]
            new_col = f"{alias}.{resolved}"

            # record mapping (hint → resolved column)
            resolved_columns_map[column_hint] = new_col

            # attach resolved column
            f["column"] = new_col

        return resolved_object, resolved_columns_map
    
    def _decide_entity_params(self, *, query_object: dict) -> dict:
        """
        Finalize entity resolution.

        - High confidence → auto-pick
        - Low/medium confidence → ask user via stdin
        - User can type entity_id or 'skip'
        """

        can_continue = True

        for idx, f in enumerate(query_object.get("filters", [])):
            resolved = f.get("resolved", [])
            hydrated = f.get("hydrated", [])
            confidence = f.get("confidence")

            # ---------- NOTHING TO RESOLVE ----------
            if not resolved:
                continue

            # ---------- HIGH CONFIDENCE ----------
            if confidence == "high":
                best_idx = max(
                    range(len(resolved)),
                    key=lambda i: resolved[i]["similarity"]
                )
                f["resolved"] = [resolved[best_idx]]
                f["hydrated"] = [hydrated[best_idx]] if hydrated else []
                continue

            # ---------- LOW / MEDIUM → ASK USER ----------
            can_continue = False

            print("\nAmbiguous entity detected:")
            print(f"  Entity type : {f.get('entity_type')}")
            print(f"  Raw value   : {f.get('raw_value')}")
            print("\nOptions:")

            seen = set()
            for i, r in enumerate(resolved):
                key = (r["entity_id"], r["surface_form"])
                if key in seen:
                    continue
                seen.add(key)

                print(
                    f"  [{i}] {r['surface_form']} "
                    f"(id={r['entity_id']}, similarity={r['similarity']:.3f})"
                )

            print("  [skip] Skip this entity filter")

            choice = input("\nChoose option index or type 'skip': ").strip()

            # ---------- USER SKIPS ----------
            if choice.lower() == "skip":
                f["resolved"] = []
                f["hydrated"] = []
                f["confidence"] = "none"
                continue

            # ---------- USER PICKS ----------
            if not choice.isdigit():
                raise ValueError("Invalid input. Expected index or 'skip'.")

            choice = int(choice)

            if choice < 0 or choice >= len(resolved):
                raise ValueError("Choice out of range.")

            f["resolved"] = [resolved[choice]]
            f["hydrated"] = [hydrated[choice]] if hydrated else []
            f["confidence"] = "high"

        query_object["continue"] = can_continue
        return query_object

    def _resolve_joins(self, *, resolved_object: dict) -> dict:
        """
        Takes the FULL resolved_object as input.
        Appends resolved_object["joins"].
        """

        tables = resolved_object.get("tables", [])

        if not tables or len(tables) < 2:
            resolved_object["joins"] = []
            return resolved_object

        joins = []

        for i in range(len(tables) - 1):
            left = tables[i]
            right = tables[i + 1]

            # direct
            if (left, right) in JOIN_GRAPH:
                joins.extend(JOIN_GRAPH[(left, right)]["joins"])
                continue

            # reverse
            if (right, left) in JOIN_GRAPH:
                joins.extend(JOIN_GRAPH[(right, left)]["joins"])
                continue

            raise ValueError(f"No join defined between {left} and {right}")

        resolved_object["joins"] = joins
        return resolved_object
    
    def _generate_sql(self, *, resolved_object: dict) -> tuple[str, list]:
        """
        Generate SQL + params from fully resolved object.
        Returns (sql, params)
        """

        base_table = resolved_object["base_table"]
        aliases = resolved_object.get("aliases", {})
        joins = resolved_object.get("joins", [])
        filters = resolved_object.get("filters", [])

        params = []
        where_clauses = []

        # ---------- FROM ----------
        base_alias = aliases.get(base_table)
        sql = f"SELECT * FROM {base_table} {base_alias}"

        # ---------- JOINS ----------
        joined_tables = set([base_table])

        for left, right in joins:
            left_tbl = left.split(".")[0]
            right_tbl = right.split(".")[0]

            # decide join direction
            if right_tbl not in joined_tables:
                sql += f"\nJOIN {right_tbl} ON {left} = {right}"
                joined_tables.add(right_tbl)
            elif left_tbl not in joined_tables:
                sql += f"\nJOIN {left_tbl} ON {left} = {right}"
                joined_tables.add(left_tbl)
            else:
                sql += f"\nAND {left} = {right}"

        # ---------- WHERE ----------
        for f in filters:
            resolved = f.get("resolved", [])
            confidence = f.get("confidence")

            # entity filter → ID based
            if confidence == "high" and resolved:
                entity_id = resolved[0]["entity_id"]
                table = resolved[0]["source_table"]
                where_clauses.append(f"{table}.id = %s")
                params.append(entity_id)
                continue

            # non-entity filter
            col = f.get("column")
            if col and f.get("raw_value") is not None:
                where_clauses.append(f"{col} {f['op']} %s")
                params.append(f["raw_value"])

        if where_clauses:
            sql += "\nWHERE " + " AND ".join(where_clauses)

        return sql, params





    
    def resume(self, *, resolved_object:dict):
        # if not resolved_object.get("continue"):
        #     return

        column_resolved = self._resolve_columns(resolved_object=resolved_object)
        self.logs["column_resolved"] = column_resolved
        
        return {
                "result": column_resolved,
                "logs":self.logs
            }

    def run(self, *, query: str, **options):
        soft_k = options.get("soft_k", 5)
        hard_k = options.get("hard_k", 7)

        print("\nNL2SQL pipeline start\n")
        print("User query:")
        print(query)

        print("\nStep 1: Query planning")
        query_planning_object = self._generate_query_planning(
            query=query,
            soft_k=soft_k,
            hard_k=hard_k
        )
        print("Planned object:")
        print(query_planning_object)

        if query_planning_object.get("skip"):
            print("\nPlanner returned skip=True")
            print("Query cannot be answered with current schema rules\n")
            return {
                "sql": None,
                "params": [],
                "reason": "planner_skip",
                "planned_object": query_planning_object
    }

        print("\nStep 2: Column resolution")
        resolved_columns, column_map = self._resolve_columns(
            resolved_object=query_planning_object
        )
        print("Resolved columns:")
        print(column_map)

        print("\nStep 3: Entity resolution")
        entity_list, resolved_object = self._resolve_entities(
            query_planning_object=resolved_columns
        )

        for f in resolved_object.get("filters", []):
            print(
                "Entity value:", f.get("raw_value"),
                "| type:", f.get("entity_type"),
                "| confidence:", f.get("confidence"),
                "| candidates:", len(f.get("resolved", []))
            )

        print("\nStep 4: Entity decision")
        resolved_object = self._decide_entity_params(
            query_object=resolved_object
        )

        if not resolved_object.get("continue"):
            print("Waiting for entity clarification from user")
        else:
            print("All entities resolved")

        print("\nStep 5: Join resolution")
        resolved_object = self._resolve_joins(
            resolved_object=resolved_object
        )
        print("Joins:")
        for j in resolved_object.get("joins", []):
            print(j)

        print("\nStep 6: SQL generation")
        sql, params = self._generate_sql(
            resolved_object=resolved_object
        )

        print("\nFinal SQL:")
        print(sql)
        print("Parameters:")
        print(params)

        print("\nSources")
        print("Tables:")
        print(resolved_object.get("tables"))

        print("\nEntities used:")
        for f in resolved_object.get("filters", []):
            if f.get("resolved"):
                r = f["resolved"][0]
                print(
                    "Entity type:", f["entity_type"],
                    "| text:", f["raw_value"],
                    "| id:", r["entity_id"]
                )

        print("\nNL2SQL pipeline end\n")

        return sql, params




        if not resolved_object.get("continue", False):
            print("Resolution needed stopping pipleine")

            return {
                "result": resolved_object,
                "logs":self.logs
            }
        
        return self.resume(resolved_object=resolved_object)
    

       

if __name__ == "__main__":

    conn = get_dev_connection()
    embedder = create_embedder()
    llm = create_groq_llm()

    guidance_store = create_guidance_store(conn=conn)
    guidance_ingestor = create_guidance_ingestor(guidance_store=guidance_store, embedder=embedder)
    guidance_retriever = create_guidance_retriever(guidance_store=guidance_store, embedder=embedder)
    entity_store = create_entity_store(conn=conn)
    entity_ingestor = create_entity_ingestor(entity_store=entity_store, embedder=embedder)
    entity_retriever = create_entity_retriever(entity_store=entity_store, embedder=embedder)
    sql_store = create_sql_store(conn=conn)
    column_store = ColumnStore(conn=conn)
    column_retriever = ColumnRetriever(column_store=column_store, embedder=embedder)
    nl2sql = NL2SQLEngine(
        llm=llm, 
        guidance_retriever=guidance_retriever, 
        entity_retriever=entity_retriever, 
        sql_store=sql_store,
        column_retriever= column_retriever
    )

    while True:
        query = input("\n\nEnter your query:\n\n")
        if not query or query == "exit":
            break

        try:
            result = nl2sql.run(query=query)
            print(result)
        except Exception as e:
            conn.rollback()
            raise e