join_rules = [
    {
  "name": "join_teacher_class_direct",
  "type": "schema_joins",
  "priority": 1,
  "active": True,
  "content": {
    "from": "teachers",
    "to": "classes",
    "path": [
      {
        "left_table": "teachers",
        "right_table": "classes",
        "on": {
          "teachers.id": "classes.class_teacher"
        }
      }
    ]
  },
  "embedding_text": "teachers can be directly linked to classes using classes.class_teacher referencing teachers.id"
}

]