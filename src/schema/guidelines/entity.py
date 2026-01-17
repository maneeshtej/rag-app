entity_rules:list[dict] = [
    {
  "name": "subject_realisation",
  "type": "entity",
  "priority": 0,

  "content": """
Detect and extract subject references from the user query when they are clearly present.

A subject reference exists when the query explicitly mentions an academic subject,
course, paper, or named academic topic.

When a subject reference is clearly present:
- Extract it as an entity with entity_type = "subject".
- raw_value MUST be the exact surface form from the user query.
- Add it to the extracted entities list.
- Do NOT treat subject mentions as plain text filters.
- Do NOT bind the subject to any table or column at this stage.

If the presence of a subject is ambiguous or uncertain, do NOT extract it.

Subject entities are resolved later to canonical representations.
""",

  "embedding_text": """
subject
academic subject
course
academic course
named course
subject name
course name
paper
curriculum
syllabus
academic topic

teaches subject
subject taught
enrolled in subject
subject offering
course offering
"""
}


,
{
  "name": "teacher_realisation",
  "type": "entity",
  "priority": 0,

  "content": """
Detect and extract teacher references from the user query when they are clearly present.

A teacher reference exists when the query explicitly refers to teaching staff,
academic personnel, instructors, professors, or individual teachers.

When a teacher reference is clearly present:
- Extract it as an entity with entity_type = "teacher".
- raw_value MUST be the exact surface form from the user query.
- Add it to the extracted entities list.
- Do NOT treat teacher references as generic users.
- Do NOT bind teacher references to any table or column at this stage.

Role-based references (e.g., "teachers", "faculty", "professors") are valid
teacher entities and should be extracted as written.

If the presence of a teacher reference is ambiguous or uncertain, do NOT extract it.

Teacher entities are resolved later to canonical representations.
""",

  "embedding_text": """
teacher
teachers
teaching staff
academic staff
faculty
faculty member
professor
lecturer
instructor

teacher name
faculty name
professor name

who teaches
who is teaching
teaches
teaching
teacher for class
teacher for subject
"""
}

,
{
  "name": "date_realisation",
  "type": "entity",
  "priority": 1,

  "content": """
Detect and extract date and time references from the user query when they are clearly present.

A date reference exists when the query explicitly mentions a specific date,
a relative date, or a time range.

When a date reference is clearly present:
- Extract it as a date constraint.
- raw_value MUST be the exact surface form from the user query.
- Normalize dates into Python-parsable ISO format (YYYY-MM-DD) when and only when
  the date can be determined with high confidence.
- start_date and end_date MUST either be:
  - valid ISO dates (YYYY-MM-DD), or
  - null if normalization is uncertain.

Do NOT invent dates.
Do NOT approximate vague expressions.
Do NOT bind date constraints to any table, column, or entity.
Do NOT infer how the date will be used later.

If the presence of a date is ambiguous or normalization is uncertain,
preserve raw_value and set both start_date and end_date to null.
""",

  "embedding_text": """
date
time
day
month
year
time period
date range

today
yesterday
tomorrow

last week
last month
last year
this week
this month
this year
next week
next month
next year

before
after
between
from
until
till

on date
on day
during period
within range
recent
recently
"""
},
{
  "name": "query_split_realisation",
  "type": "entity",
  "priority": 2,
  "content": """
Detect when a user query contains multiple independent requests that should be split into separate semantic sub-queries.

A split is REQUIRED when:
- The query contains coordinating conjunctions such as "and", "also", "then", "as well as".
- Each clause expresses an independent intent that can be answered on its own.
- Each clause targets different actions, intents, or primary entities.

When splitting:
- Produce one sub-query per independent clause.
- Each sub-query MUST be a complete, standalone question.
- Each sub-query MUST include only the entities relevant to that clause.
- Do NOT duplicate entities across sub-queries unless they are explicitly shared.

Do NOT split when:
- The conjunction joins multiple entities for the same intent (e.g. "subjects taught by A and B").
- The conjunction refines or elaborates a single request.

If splitting is ambiguous, DO NOT split.
""",
  "embedding_text": """
and
also
then
as well as
along with
separately
another
additionally
in addition
next
after that
first
second
multiple requests
separate queries
two questions
more than one task
"""
}
]