rules: list[dict] = [
   {
    "name": "department_realisation",
    "type": "rule",
    "priority": 0,
    "content": """
    Whenever the user query contains any department-indicating word,
    explicitly extract the department reference as an entity.

    Department-indicating words include, but are not limited to:
    cs, cse, computer science, computer department,
    it, information technology,
    ece, electronics,
    ee, electrical,
    mech, mechanical,
    civil,
    department, branch, academic department.

    If a department reference is present, it MUST be added to the
    SQL planning object's entity list as a department entity using
    the exact natural language value from the user query.

    Do not treat department mentions as plain text filters.
    They must be resolved later to a canonical department
    representation (department_id or department_name).
    """,

    "embedding": """
    computer science department
    cs department
    computer department
    information technology branch
    it department
    electronics and communication department
    ece branch
    mechanical engineering department
    mech department
    civil engineering department
    academic department
    department
    branch
    from departments
    in departments
    inluding departments
    """
}      ,
{
  "name": "subject_realisation",
  "type": "rule",
  "priority": 0,
  "content": """
  Whenever the user query contains any subject-indicating word,
  explicitly extract the subject reference as an entity.

  Subject-indicating words include, but are not limited to:
  subject, course, paper,
  operating systems, os,
  data structures, dsa,
  database systems, dbms,
  computer networks, cn,
  machine learning, ml,
  artificial intelligence, ai,
  software engineering,
  compiler design,
  theory of computation,
  mathematics, physics, chemistry.

  If a subject reference is present, it MUST be added to the
  SQL planning object's entity list as a subject entity using
  the exact natural language value from the user query.

  Do not treat subject mentions as plain text filters.
  They must be resolved later to a canonical subject
  representation (subject_id or subject_name).
  """,

  "embedding": """
  operating systems subject
  os subject
  data structures subject
  dsa course
  database systems subject
  dbms paper
  computer networks subject
  cn course
  machine learning subject
  ml subject
  artificial intelligence subject
  ai course
  software engineering subject
  compiler design subject
  theory of computation subject
  subject
  course
  paper
  from subject
  who teach subject
  who look over subject
  """
},
{
  "name": "faculty_realisation",
  "type": "rule",
  "priority": 0,
  "content": """
  Whenever the user query refers to teaching staff or academic personnel,
  explicitly extract the referenced people as faculty-related entities.

  Faculty-indicating words include, but are not limited to:
  faculty, faculty member, professor, lecturer, teacher, teaching staff.

  If the query implies a role-based group (for example, \"faculty members\",
  \"teachers\", or \"professors\") rather than a specific name, the entity MUST
  still be extracted as a faculty entity.

  If a specific faculty name is mentioned, it MUST be extracted exactly
  as written in the query as a faculty entity.

  Faculty references MUST be resolved to canonical faculty representations
  stored in the faculty table (such as faculty_id or faculty.name).

  Do NOT map faculty references to generic users unless explicitly requested.
  """,
  "embedding": """
  faculty
  faculty members
  professors
  professor
  lecturers
  teachers
  teaching staff
  who teaches
  who teaches subject
  list faculty
  list teachers
  faculty teaching subject
  faculty working in department
  """
},

{
  "name": "comparison_realisation",
  "type": "rule",
  "priority": 1,
  "content": """
  Whenever the user query contains comparison expressions
  (such as greater than, less than, at least, at most, equal to),
  extract them as comparison constraints.

  Comparison-indicating phrases include:
  more than, greater than, above,
  less than, below,
  at least, minimum,
  at most, maximum,
  equal to, exactly.

  The comparison MUST be extracted with:
  - operator (>, <, >=, <=, =)
  - numeric value (as mentioned in the query)

  Do not decide which column the comparison applies to.
  That decision must be deferred to SQL planning.
  """,

  "embedding": """
  more than
  greater than
  less than
  at least
  at most
  equal to
  exactly
  above
  below
  """
},
{
  "name": "date_realisation",
  "type": "rule",
  "priority": 1,
  "content": """
  Whenever the user query refers to dates or time ranges,
  extract them as normalized date constraints.

  Date-indicating phrases include:
  today, yesterday, tomorrow,
  last week, last month, last year,
  before <date>, after <date>, between <date> and <date>.

  The extracted date constraint MUST include:
  - start_date (if applicable)
  - end_date (if applicable)

  Do not bind the date to any specific table or column.
  Date resolution must be handled later during SQL planning.
  """,

  "embedding": """
  today
  yesterday
  last week
  last month
  last year
  before
  after
  between
  from date
  till date
  """
},
{
  "name": "existence_intent_realisation",
  "type": "rule",
  "priority": 2,
  "content": """
  Whenever the user query asks whether something exists, is present,
  or is available, explicitly extract the intent as an existence check.

  Existence-indicating phrases include, but are not limited to:
  is there,
  does exist,
  exists,
  present or not,
  available,
  found,
  can I find,
  do we have,
  whether there is,
  is any,
  are there any.

  If the query is phrased as a yes/no question, it MUST be treated
  as an existence intent even if no explicit existence keyword
  is present.

  The existence intent MUST be represented explicitly in the
  normalized query structure (for example, intent = "exists").

  Do NOT decide how existence is checked in SQL.
  Do NOT choose between COUNT, EXISTS, or LIMIT-based checks.
  Those decisions must be deferred to deterministic SQL planning.
  """,

  "embedding": """
  is there
  does exist
  exists
  present or not
  available
  found
  can i find
  do we have
  whether there is
  is any
  are there any
  is a user present
  does a record exist
  is there a faculty
  is subject available
  """
},
{
  "name": "query_splitting_realisation",
  "type": "rule",
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

