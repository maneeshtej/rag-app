generate_rules:list[dict] = [
   {
    "name": "faculty_subject_generation",
    "type": "generate_rules",
    "priority": 0,

    "content": """
    Trigger when the query asks about a teaching relationship
    between faculty and subjects.

    This includes:
    - who teaches a subject
    - which faculty handles a subject
    - what subjects a faculty member teaches
    - courses handled by a teacher or instructor

    When triggered:
    - treat this as a faculty–subject relationship query
    - DO NOT answer from only one table
    - JOIN faculty and subjects using the relationship defined in the schema
    - ensure the result includes context from both faculty and subject
    - avoid isolated lists that hide the teaching relationship
    - prefer complete relational rows over partial entity outputs

    Joins MUST follow the schema.
    This rule does not permit inventing joins or tables.
    """,

    "embedding_text": """
        who teaches subject
        which faculty handles subject
        what subjects does faculty teach
        subjects taught by teacher
        courses handled by instructor

        faculty subject join
        join faculty subjects
        faculty subjects relationship
        teaching assignment join
        faculty subject mapping

        avoid isolated subject list
        avoid isolated faculty list
        relationship query
        """
    }
    ,
    {
    "name": "faculty_full_context_generation",
    "type": "generate_rules",
    "priority": 1,

    "content": """
    Trigger when the user asks about faculty directly.

    This includes queries asking:
    - about a specific faculty member
    - for faculty details or profile
    - to list faculty
    - to identify faculty involved in any role

    When triggered:
    - treat the query as faculty-centric
    - include ALL meaningful faculty fields available in the schema
    - prefer full faculty records over minimal projections
    - avoid returning only identifiers or partial faculty information

    If the query also involves other entities (subject, department):
    - faculty remains the primary focus
    - other entities provide supporting context

    Joins MUST follow the schema.
    This rule does not permit inventing tables or fields.
    """,

    "embedding_text": """
    faculty details
    faculty information
    faculty profile
    faculty full details
    faculty complete record

    about faculty
    show faculty
    list faculty
    find faculty
    faculty member details

    professor details
    lecturer details
    assistant professor details
    associate professor details
    instructor details

    faculty contact information
    faculty email
    faculty designation
    faculty department
    faculty experience
    """
    }
    ,
    {
    "name": "subject_full_context_generation",
    "type": "generate_rules",
    "priority": 1,

    "content": """
    Trigger when the user asks about subjects directly.

    This includes queries asking:
    - about a specific subject or course
    - to list subjects
    - for subject details or curriculum information
    - to identify subjects handled, offered, or available

    When triggered:
    - treat the query as subject-centric
    - include ALL meaningful subject fields available in the schema
    - prefer full subject records over minimal projections
    - avoid returning only identifiers or partial subject information

    If the query also involves other entities (faculty, department):
    - subject remains the primary focus
    - other entities provide supporting context

    Joins MUST follow the schema.
    This rule does not permit inventing tables or fields.
    """,

    "embedding_text": """
    subject details
    subject information
    subject profile
    subject full details
    subject complete record

    about subject
    show subject
    list subjects
    find subject
    course details
    course information

    subject code
    subject name
    subject credits
    subject department
    curriculum subject
    academic subject

    courses offered
    subjects offered
    """
    }
]