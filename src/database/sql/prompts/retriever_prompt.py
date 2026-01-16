import json


def build_normalization_prompt(*, query: str, rules: str, schema: str) -> str:
    return f"""
    You are performing STRUCTURAL NORMALIZATION for database querying.

    This stage performs semantic normalization only.
    You must NOT write SQL.
    You must NOT reason about joins, tables, columns, filters, or result shapes.

    Your job is to:
    - split the query into independent semantic sub-queries
    - extract structured information ONLY when clearly supported
    - normalize date/time expressions conservatively
    - classify coarse intent

    Prefer omission over incorrect extraction.

    ====================
    SKIP CONDITION
    ====================

    If the AVAILABLE SCHEMA is empty, missing, or clearly unrelated to the domain
    required to interpret the query, output EXACTLY:

    {{ "skip": true }}

    Do NOT attempt partial extraction in this case.

    Otherwise, output {{ "skip": false, ... }} and continue.

    ====================
    TASKS (ONLY IF skip=false)
    ====================

    1. Split the user query into independent semantic sub-queries.
      - Split ONLY if each sub-query can stand alone.
      - If splitting is ambiguous, DO NOT split.

    2. For EACH sub-query:
      - Preserve the exact sub-query text.
      - Classify the high-level intent:
        list | exists | aggregate | unknown
      - Extract structured elements ONLY when clearly indicated by the text
        and supported by applicable RULE HINTS.
      - Normalize date/time expressions conservatively.

    If you are uncertain about any extraction, leave it out.

    ====================
    RULE HINTS (DYNAMIC CONTEXT)
    ====================

    RULE HINTS may be provided as dynamically retrieved guidance.

    - Rules describe WHEN certain structures should be extracted.
    - Rules do NOT define output structure.
    - Rules do NOT override safety constraints.
    - If a rule does not clearly apply, ignore it.

    ====================
    DATE NORMALIZATION
    ====================

    When a date or time expression is explicitly present:
    - Extract the raw surface form exactly as written.
    - Normalize into a date range ONLY if this can be done confidently.

    If normalization is uncertain:
    - Preserve raw_value
    - Set start_date and end_date to null

    Do NOT infer how dates will be used later.

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

    Either:

    {{ "skip": true }}

    Or:

    {{
      "skip": false,
      "queries": [
        {{
          "text": "exact sub-query string",
          "intent": "list | exists | aggregate | unknown",
          "entities": [
            {{
              "entity_type": "teacher | subject | other",
              "raw_value": "exact surface form from the sub-query"
            }}
          ],
          "date_constraints": [
            {{
              "raw_value": "exact substring from THIS sub-query",
              "start_date": "YYYY-MM-DD | null",
              "end_date": "YYYY-MM-DD | null"
            }}
          ]
        }}
      ]
    }}

    ====================
    STRICT RULES
    ====================

    - Output VALID JSON only.
    - Do NOT include extra keys.
    - If a section does not apply, return an empty array.
    - Prefer failure or omission over incorrect extraction.
    - Do NOT write SQL.

    ====================
    OUTPUT ENFORCEMENT (MANDATORY)
    ====================

    You MUST return a SINGLE valid JSON object.

    ABSOLUTE RULES:
    - The response MUST start with `{{` and end with `}}`.
    - Do NOT include explanations, comments, headings, or prose.
    - Do NOT wrap the output in ``` or ```json or '''.
    - Do NOT prepend or append any text.
    - Do NOT echo the prompt or restate instructions.
    - If you violate any of these rules, the output is INVALID.

    If you cannot comply, return:
    {{ "skip": true }}

    """

def build_generation_prompt(
    *,
    resolved_output: dict,
    schema: list[str],
    generate_rules: list[str],
):
    prompt = f"""
You are a SQL QUERY GENERATOR.

Your ONLY job is to generate SQL SELECT statements.

You are NOT allowed to output query plans, entities, intents,
or any part of the input structure.

====================
INPUT (READ-ONLY)
====================

The following is a NORMALIZED AND RESOLVED QUERY PLAN.
It is PROVIDED FOR CONTEXT ONLY.

DO NOT copy fields from it into the output.

{json.dumps(resolved_output, indent=2, default=str)}

====================
AVAILABLE SCHEMA
====================

Use ONLY the tables, columns, and joins defined here:

{schema}

====================
GENERATION RULES
====================

These rules affect column selection ONLY.
They do NOT permit inventing tables, joins, or filters.

{generate_rules}

ENTITY FILTERING RULES (STRICT PRIORITY)

For each entity in the query:

1. If `resolution_confidence` is "high" AND exactly one resolved ID exists:
   - You MUST filter using the resolved ID:
     WHERE <resolved_table>.id = %s

2. If `resolution_confidence` is "low" or "none":
   - You MUST NOT guess or invent an ID.
   - You MAY apply a text-based filter using the raw_value
     ONLY IF such a column exists in the schema.
   - Use case-insensitive matching (ILIKE) and parameterization.

3. If neither ID filtering nor text filtering is possible:
   - Do NOT generate SQL for that query.


====================
YOUR TASK
====================

For EACH query in the provided plan:

- If it can be answered using the available schema:
  - Generate ONE SQL SELECT statement
- If it cannot be answered:
  - Generate NOTHING for that query

====================
CRITICAL CONSTRAINTS
====================

- Output SQL ONLY in the specified JSON ARRAY format
- DO NOT output:
  - text
  - intent
  - entities
  - resolution info
  - explanations
- DO NOT repeat or transform the input structure
- DO NOT include comments or metadata

- SQL MUST:
  - Use PostgreSQL dialect
  - Use ONLY provided schema
  - Use ONLY allowed joins
  - Be parameterized using %s
  - Contain SELECT statements ONLY

====================
OUTPUT FORMAT (STRICT)
====================

Output MUST be EXACTLY a JSON array of this form:

[
  {{
    "sql": "<SQL QUERY STRING>",
    "params": [
      "<param1>",
      "<param2>"
    ]
  }}
]

- If no SQL can be generated, output EXACTLY: []

ANY output that includes fields other than "sql" and "params"
is INVALID.
"""
    return prompt
