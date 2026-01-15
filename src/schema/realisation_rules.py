realisation_rules: list[dict] = [
{
  "name": "subject_realisation",
  "type": "realisation_rules",
  "priority": 0,

  "content": """
You MUST detect and extract subject references from the user query.

A subject reference exists whenever the query mentions an academic subject,
course, paper, or named topic that maps to a subject.

When a subject reference is present:
- Extract it as an entity with entity_type = "subject".
- The extracted value MUST be the exact surface form from the user query.
- Add it to the SQL planning object's entity list.
- Do NOT treat subject mentions as plain text filters.
- Do NOT bind the subject to any table or column at this stage.

Subject entities MUST be resolved later to a canonical representation
(subject_id or subject_name).

Failure to extract a subject entity when present is an error.
""",

  "embedding_text": """
subject
course
paper
academic subject

operating systems
os
operating system course

data structures
dsa
data structures course

database systems
dbms
database subject

computer networks
cn
networking subject

machine learning
ml
machine learning course

artificial intelligence
ai
ai subject

software engineering
se
software engineering course

compiler design
compiler
compiler course

theory of computation
toc
automata

mathematics
maths
physics
chemistry

teach subject
teaches subject
subject taught by
faculty teaching subject
who teaches
enrolled in subject
"""
}
,
{
  "name": "teacher_realisation",
  "type": "realisation_rules",
  "priority": 0,

  "content": """
You MUST detect and extract teacher references from the user query.

A teacher reference exists whenever the query refers to teaching staff,
academic personnel, instructors, professors, or individual teachers.

When a teacher reference is present:
- Extract it as an entity with entity_type = "teacher".
- The extracted value MUST be the exact surface form from the user query.
- Add it to the SQL planning object's entity list.
- If the reference is role-based (e.g., "teachers", "faculty", "professors"),
  it MUST still be extracted as a teacher entity.
- Do NOT treat teacher references as generic users.
- Do NOT bind teacher references to any table or column at this stage.

If a specific teacher name is mentioned, extract the name exactly as written.

Teacher entities MUST be resolved later to canonical representations
stored in the teachers table (teachers.id or teachers.name).

Failure to extract a teacher entity when present is an error.
""",

  "embedding_text": """
teacher
teachers
faculty
faculty member
professor
professors
lecturer
lecturers
instructor
instructors
teaching staff

teacher name
faculty name
professor name

who teaches
who is teaching
teacher for class
teacher for subject

list teachers
show teachers
find teacher
search teacher

teachers in class
teachers teaching subject
teacher assigned to class
"""
}
,
{
  "name": "date_realisation",
  "type": "realisation_rules",
  "priority": 1,

  "content": """
You MUST detect and extract date and time references from the user query.

A date reference exists whenever the query mentions a specific date,
a relative date, or a time range.

When a date reference is present:
- Extract it as a date constraint.
- You MUST extract:
  - start_date (if applicable)
  - end_date (if applicable)
  - the raw date phrase exactly as it appears in the query
- Do NOT bind date constraints to any table, column, or entity.
- Do NOT infer how the date will be used in SQL.

Date constraints MUST remain unbound until deterministic SQL planning.

Failure to extract a date constraint when present is an error.
""",

  "embedding_text": """
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

before date
after date
between dates
from date
till date

on date
on day
during period
within range
in the past
recent
recently
"""
}
]



