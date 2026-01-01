rules: list[dict] = [
    {
        "name": "department_realisation",
        "type": "query_rule",
        "priority": 0,
        "content": """
        Before generating SQL, identify when the user is referring to an academic
        department in the query, even if it is mentioned indirectly or informally
        (for example, "CS", "computer dept", or "IT branch").

        Resolve the referenced department to its canonical database representation
        (such as department_id or department_name) instead of treating it as raw text.
        """,

        "embedding": """
        Queries where users refer to departments using informal names, abbreviations,
        or context rather than exact database values.

        This includes questions about exam schedules, timetables, subjects, or faculty
        that are scoped to a specific department without explicitly naming the
        department column or identifier.

        The intent is to correctly map natural language department references to
        structured department entities before SQL generation.
        """
    }
]

