realisation_rules: list[dict] = [
   {
      "name": "department_realisation",
      "type": "realisation_rules",
      "priority": 0,

      "content": """
    You MUST detect and extract department references from the user query.

    A department reference exists whenever the query mentions any academic department,
    branch, or field of study that maps to a department.

    When a department reference is present:
    - Extract it as an entity with entity_type = "department".
    - The extracted value MUST be the exact surface form from the user query.
    - Add it to the SQL planning object's entity list.
    - Do NOT treat department mentions as plain text filters.
    - Do NOT bind the department to a table or column at this stage.

    Department entities MUST be resolved later to a canonical representation
    (department_id or department_name).

    Failure to extract a department entity when present is an error.
    """,

      "embedding_text": """
    department
    academic department
    branch
    field
    stream
    specialization

    computer science
    computer science department
    cs
    cse
    computer department

    information technology
    it
    it department

    electronics
    electronics department
    ece
    electrical
    ee

    mechanical
    mechanical engineering
    mech
    mechanical department

    civil
    civil engineering
    civil department

    from department
    in department
    of department
    department of
    branch of
    belonging to department
    working in department
    faculty of department
    students of department
    """
    },
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
  "name": "faculty_realisation",
  "type": "realisation_rules",
  "priority": 0,

  "content": """
You MUST detect and extract faculty references from the user query.

A faculty reference exists whenever the query refers to teaching staff,
academic personnel, or individual instructors.

When a faculty reference is present:
- Extract it as an entity with entity_type = "faculty".
- The extracted value MUST be the exact surface form from the user query.
- Add it to the SQL planning object's entity list.
- If the reference is role-based (e.g., "faculty", "teachers", "professors"),
  it MUST still be extracted as a faculty entity.
- Do NOT treat faculty references as generic users.
- Do NOT bind faculty references to any table or column at this stage.

If a specific faculty name is mentioned, extract the name exactly as written.

Faculty entities MUST be resolved later to canonical representations
stored in the faculty table (faculty_id or faculty.name).

Failure to extract a faculty entity when present is an error.
""",

  "embedding_text": """
faculty
faculty member
faculty members

professor
professors
lecturer
lecturers
teacher
teachers
teaching staff
instructor
instructors

who teaches
who teaches subject
who teaches course
faculty teaching subject
faculty teaching course

list faculty
list teachers
show faculty
faculty list

faculty working in department
faculty of department
teachers in department
professors in department

taught by
handled by
under professor
under faculty
"""
},


{
  "name": "comparison_realisation",
  "type": "realisation_rules",
  "priority": 1,

  "content": """
You MUST detect and extract comparison expressions from the user query.

A comparison expression exists whenever the query compares a quantity,
count, value, or measurement using relational language.

When a comparison expression is present:
- Extract it as a comparison constraint.
- You MUST extract:
  - the comparison operator (>, <, >=, <=, =)
  - the compared value exactly as stated in the query
  - the raw comparison phrase as it appears in the query
- Do NOT decide which table or column the comparison applies to.
- Do NOT bind the comparison to any entity, attribute, or schema element.

Comparison constraints MUST remain unbound until deterministic SQL planning.

Failure to extract a comparison expression when present is an error.
""",

  "embedding_text": """
more than
greater than
above
over
exceeding
higher than

less than
below
under
lower than

at least
minimum
no less than

at most
maximum
no more than

equal to
equals
exactly
is equal to

greater than or equal to
less than or equal to
>=
<=
>
<
=

more than 5
less than 10
at least 3
at most 20
exactly 1
"""
},
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
,
{
  "name": "existence_intent_realisation",
  "type": "realisation_rules",
  "priority": 2,

  "content": """
You MUST detect and extract existence intent from the user query.

An existence intent exists whenever the query asks whether something
exists, is present, is available, or can be found.

When an existence intent is present:
- Extract the intent explicitly as intent = "exists".
- Treat yes/no questions as existence intent even if no explicit
  existence keyword is used.
- Do NOT decide how existence is evaluated in SQL.
- Do NOT choose between COUNT, EXISTS, LIMIT, or aggregation strategies.
- Do NOT bind existence intent to any table, column, or entity.

Existence intent MUST remain abstract until deterministic SQL planning.

Failure to extract existence intent when present is an error.
""",

  "embedding_text": """
is there
are there
is any
are there any

exists
does exist
does it exist
exist or not

present
present or not
available
availability
found
can be found

can i find
do we have
whether there is
whether exists

is there a
is there any
is subject available
is faculty present
does a record exist
"""
}
,
{
  "name": "query_splitting_realisation",
  "type": "realisation_rules",
  "priority": 3,
  "content": """
  When the user query explicitly contains multiple independent
  requests joined by conjunctions, split the query into
  separate sub-queries.

  Conjunction-indicating words include, but are not limited to:
  and,
  also,
  as well as,
  along with,
  plus,
  additionally.

  A query MUST be split ONLY IF:
  - each part can stand as a complete query on its own, and
  - no part depends on the result of another part.

  The split queries MUST preserve the original phrasing
  of each sub-query without reinterpretation.

  Do NOT split queries when:
  - conjunctions are used only as filters
    (e.g., "faculty teaching math and physics"),
  - the query requires shared joins or shared aggregations,
  - the query implies a single combined result.

  Query splitting MUST be declarative only.
  Do NOT decide execution order, joins, or result merging.
  Those decisions must be handled later by deterministic planning.
  """,

  "embedding": """
  and
  also
  as well as
  along with
  plus
  additionally
  list users and count admins
  show departments and subjects
  list faculty and list students
  get users and also show departments
  """
}
]



