JOIN_GRAPH = {
    ("teachers", "classes"): {
        "via": "class_teachers",
        "joins": [
            ("teachers.id", "class_teachers.teacher_id"),
            ("class_teachers.class_id", "classes.id"),
        ],
    },

    ("classes", "teachers"): {  # reverse lookup
        "via": "class_teachers",
        "joins": [
            ("classes.id", "class_teachers.class_id"),
            ("class_teachers.teacher_id", "teachers.id"),
        ],
    },
    # classes -> subjects
("classes", "subjects"): {
    "via": "class_subjects",
    "joins": [
        ("classes.id", "class_subjects.class_id"),
        ("class_subjects.subject_id", "subjects.id"),
    ],
},

# subjects -> classes (reverse)
("subjects", "classes"): {
    "via": "class_subjects",
    "joins": [
        ("subjects.id", "class_subjects.subject_id"),
        ("class_subjects.class_id", "classes.id"),
    ],
},
("teachers", "subjects"): {
    "via": ["class_teachers", "classes", "class_subjects"],
    "joins": [
        ("teachers.id", "class_teachers.teacher_id"),
        ("class_teachers.class_id", "classes.id"),
        ("classes.id", "class_subjects.class_id"),
        ("class_subjects.subject_id", "subjects.id"),
    ],
},
("subjects", "teachers"): {
    "via": ["class_subjects", "classes", "class_teachers"],
    "joins": [
        ("subjects.id", "class_subjects.subject_id"),
        ("class_subjects.class_id", "classes.id"),
        ("classes.id", "class_teachers.class_id"),
        ("class_teachers.teacher_id", "teachers.id"),
    ],
},

}

def resolve_joins(resolved_object: dict) -> dict:
    """
    Takes the FULL resolved_object as input.
    Appends resolved_object["joins"].
    """

    tables = [t["name"] for t in resolved_object.get("tables", [])]

    if len(tables) < 2:
        resolved_object["joins"] = []
        return resolved_object

    joins = []

    for i in range(len(tables) - 1):
        left = tables[i]
        right = tables[i + 1]

        # try direct
        key = (left, right)
        if key in JOIN_GRAPH:
            joins.extend(JOIN_GRAPH[key]["joins"])
            continue

        # try reverse
        rev_key = (right, left)
        if rev_key in JOIN_GRAPH:
            joins.extend(JOIN_GRAPH[rev_key]["joins"])
            continue

        raise ValueError(f"No join defined between {left} and {right}")

    resolved_object["joins"] = joins
    return resolved_object



if __name__ == "__main__":

    # ---------- TEST CASES ----------

    tests = [
        {
            "name": "teachers -> subjects (full object)",
            "input": {
                "skip": False,
                "intent": "list",
                "tables": [
                    {
                        "name": "subjects",
                        "columns": ["subject_name", "subject_code"],
                        "aggregates": None,
                    },
                    {
                        "name": "teachers",
                        "columns": ["name", "email"],
                        "aggregates": None,
                    },
                ],
                "filters": [
                    {
                        "op": "=",
                        "entity_type": "teacher",
                        "raw_value": "sujatha joshi",
                        "confidence": "high",
                    }
                ],
                "limit": None,
                "continue": True,
            },
            "expected": [
                ("teachers.id", "class_teachers.teacher_id"),
                ("class_teachers.class_id", "classes.id"),
                ("classes.id", "class_subjects.class_id"),
                ("class_subjects.subject_id", "subjects.id"),
            ],
        }
    ]

    # ---------- RUN TESTS ----------

    for test in tests:
        print(f"\nTEST: {test['name']}")
        try:
            obj = test["input"]

            result_obj = resolve_joins(obj)
            result = result_obj.get("joins", [])

            print("Result joins:")
            for j in result:
                print("  ", j)

            assert result == test["expected"]
            print("STATUS: ✅ PASS")

        except Exception as e:
            print("STATUS: ❌ FAIL")
            print("ERROR:", e)

