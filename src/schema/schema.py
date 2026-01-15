from src.models.user import User

schema = [
    {
        "name": "events",
        "type": "schema_guidance",
        "priority": 3,
        "active": True,

        "content": """
        This guidance defines the EVENTS table.

        Use this table when the user asks about academic or administrative events that occur within a time window.

        EVENTS represent:
        - exams, assignments, holidays, notices, announcements, circulars
        - academic calendar entries
        - upcoming, ongoing, or past events bounded by start_time and end_time

        Columns:
        - id: unique identifier of the event
        - title: name or heading of the event
        - event_type: category such as exam, holiday, assignment, notice, announcement
        - start_time: datetime when the event starts
        - end_time: datetime when the event ends
        - subject_id: link to subjects table
        - file_id: source document reference
        - metadata: additional structured or unstructured details

        Joins:
        - events.subject_id → subjects.id
        - events.file_id → files.id

        Filtering rules:
        - Use start_time and end_time for date range queries
        - Filter by subject_id for subject-specific events
        - event_type is used to distinguish exams, holidays, assignments, and notices
        """,

            "embedding_text": """
        events table academic events administrative events university events college events

        exam schedule exam dates mid semester exam end semester exam internal exam external exam
        assignment deadline assignment submission due date last date to submit
        holiday list public holiday academic holiday university holiday
        notices announcements circulars official notice schedule update reschedule cancellation

        academic calendar timetable semester calendar important dates
        upcoming events ongoing events past events
        events today events this week events this month
        events between dates events in date range

        subject wise events subject related exams assignments
        events related to a subject

        when is the exam
        what events are coming up
        show upcoming academic events
        list holidays this month
        what assignments are due
        events for a specific subject
        """
    }
    ,
    {
    "name": "subjects",
    "type": "schema_guidance",
    "priority": 4,
    "active": True,

    "content": """
    This guidance defines the SUBJECTS table.

    Use this table when the user refers to academic subjects or courses
    that are part of a curriculum or timetable.

    SUBJECTS represents individual subjects such as
    Data Structures, Operating Systems, DBMS, Mathematics, etc.

    Table schema:
    - id: unique subject identifier (UUID)
    - subject_code: official subject or course code
    - subject_name: full subject name

    Semantics:
    - Each row represents exactly one subject
    - subject_code uniquely identifies a subject within an institution
    - subject_name is the human-readable name of the subject

    Resolution rules:
    - Resolve subjects using subject_code when available
    - Otherwise resolve using subject_name

    Usage notes:
    - SUBJECTS stores only subject identity information
    - Relationships to faculty, classes, or timetables are handled
      through separate relationship tables
    """,

    "embedding_text": """
    subjects table
    academic subjects
    courses offered
    subject list
    list of subjects

    subject code
    course code
    subject identifier

    subject name
    course name

    data structures
    operating systems
    dbms
    mathematics
    physics
    chemistry

    subjects in timetable
    subjects in curriculum
    """
}

    ,
    {
    "name": "teachers",
    "type": "schema_guidance",
    "priority": 4,
    "active": True,

    "content": """
    This guidance defines the TEACHERS table.

    Use this table when the user refers to teachers, faculty members,
    instructors, professors, or teaching staff.

    TEACHERS represents individual teaching staff of the institution.

    Table schema:
    - id: unique teacher identifier (UUID)
    - name: full name of the teacher
    - email: official or known email address (nullable)

    Semantics:
    - Each row represents exactly one teacher
    - name is the primary human identifier
    - email, when present, is unique per teacher

    Resolution rules:
    - Resolve teachers using email when available
    - Otherwise resolve using name
    - Do not infer designation, department, or experience

    Usage notes:
    - TEACHERS stores only teacher identity information
    - Subject assignments, classes, and schedules are handled
      through separate relationship tables
    """,

    "embedding_text": """
    teachers table
    teacher
    teachers
    faculty
    instructor
    professor
    lecturer
    teaching staff

    teacher name
    faculty name
    instructor name

    teacher email
    faculty email

    list teachers
    find teacher
    search faculty member
    """
}
,
{
    "name": "classes",
    "type": "schema_guidance",
    "priority": 4,
    "active": True,

    "content": """
    This guidance defines the CLASSES table.

    Use this table when the user refers to scheduled class sessions,
    lectures, labs, or periods that occur at a specific time and day.

    CLASSES represents individual timetable entries, not abstract
    academic groups or grade levels.

    Table schema:
    - id: unique class session identifier (UUID)
    - class_name: name or identifier of the class (e.g. "10A", "CS-3", "B.Tech CSE")
    - day_of_week: day on which the class occurs (e.g. Monday, Tuesday)
    - start_time: class start time
    - end_time: class end time
    - type: class type (e.g. Lecture, Lab, Tutorial)
    - room: room or location (nullable)
    - label: optional short label for the class
    - notes: additional notes or remarks (nullable)

    Semantics:
    - Each row represents one scheduled class session
    - A class is uniquely identified by class_name + day_of_week + time
    - This table is time-bound and event-like in nature

    Resolution rules:
    - Resolve class sessions using class_name, day_of_week, start_time, and end_time
    - Do not collapse multiple days or times into a single row
    - Do not infer teachers or subjects from this table alone

    Usage notes:
    - CLASSES stores scheduling information only
    - Relationships to teachers or subjects are handled via
      separate relationship tables
    """,
    

    "embedding_text": """
    classes table
    class schedule
    timetable
    class session
    lecture schedule
    lab schedule

    class name
    class section
    class group

    day of week
    class day
    monday tuesday wednesday thursday friday

    start time
    end time
    class timing
    period time

    lecture
    lab
    tutorial

    classroom
    room number

    timetable entry
    scheduled class
    """
},
{
  "name": "day_time_realisation",
  "type": "realisation_rules",
  "priority": 1,

  "content": """
You MUST detect and extract day-of-week and time references
from the user query when present.

A day-of-week reference exists whenever the query mentions
a weekday explicitly or implicitly.

A time reference exists whenever the query mentions a specific
time or time range.

When such references are present:
- Extract day_of_week as a string
  (e.g. "Monday", "Tuesday").
- Extract start_time and end_time when a time range is mentioned.
- Preserve the raw surface phrases as written in the query.

Do NOT treat days or times as entities.
Do NOT bind them to any table or column at this stage.
Do NOT infer schedule structure or joins.

These values MUST remain unbound constraints until
deterministic SQL planning.
""",

  "embedding_text": """
monday
tuesday
wednesday
thursday
friday
saturday
sunday

today
tomorrow
yesterday

morning
afternoon
evening

at 9
9 am
10 am
between 9 and 11
from 10 to 12
before 11
after 2

first period
second period
last period

class time
period time
lecture time
"""
}
,
{
    "name": "class_subjects",
    "type": "schema_guidance",
    "priority": 5,
    "active": True,

    "content": """
    This guidance defines the CLASS_SUBJECTS table.

    Use this table to represent the relationship between
    scheduled class sessions and academic subjects.

    CLASS_SUBJECTS links one class session to one subject.

    Table schema:
    - id: unique relationship identifier (UUID)
    - class_id: references classes.id
    - subject_id: references subjects.id

    Semantics:
    - Each row represents one subject being taught
      in one specific class session
    - This is a pure relationship table
    - No additional attributes are stored here

    Resolution rules:
    - Do NOT resolve using text or embeddings
    - class_id and subject_id must already exist
    - Insert only after both classes and subjects
      have been resolved and assigned IDs

    Usage notes:
    - CLASS_SUBJECTS contains no timing, teacher,
      or room information
    - Avoid duplicate entries for the same
      (class_id, subject_id) pair
    """,

    "embedding_text": """
    class subjects
    class subject mapping
    subject taught in class
    subject for a class

    class to subject relationship
    timetable subject mapping

    which subject is taught in this class
    subject assigned to class
    """
}
,
{
    "name": "class_teachers",
    "type": "schema_guidance",
    "priority": 5,
    "active": True,

    "content": """
    This guidance defines the CLASS_TEACHERS table.

    Use this table to represent which teacher teaches
    a specific scheduled class session.

    CLASS_TEACHERS links teachers to individual
    class timetable entries.

    Table schema:
    - id: unique relationship identifier (UUID)
    - class_id: references classes.id
    - teacher_id: references teachers.id
    - role: optional role of the teacher in the class
      (e.g. "Instructor", "Lab Assistant", "Co-Teacher")

    Semantics:
    - Each row represents one teacher assigned to one
      specific class session
    - Multiple teachers may be assigned to the same class
      (e.g. labs, team teaching)
    - A teacher may appear in many class sessions

    Resolution rules:
    - Do NOT resolve using text or embeddings
    - class_id and teacher_id must already exist
    - Insert only after both classes and teachers
      have been resolved and assigned IDs

    Usage notes:
    - CLASS_TEACHERS is time-bound and schedule-specific
    - Do not infer subjects from this table
    - Avoid duplicate entries for the same
      (class_id, teacher_id, role) combination
    """,

    "embedding_text": """
    class teachers
    teacher assigned to class
    teacher for class session
    who teaches this class

    class teacher mapping
    timetable teacher assignment

    teacher role in class
    instructor
    lab assistant
    co teacher
    """
}
]




# schema = {
#     "events": """

#     academic events administrative events university events college events

# exam schedule exam dates mid exam end exam internal exam
# assignment deadlines submissions due dates
# holiday list public holidays academic holidays
# notices announcements circulars schedule changes

# academic calendar calendar timetable
# upcoming events events this week events this month events this
# events between dates important events

# department events department wise events
# subject events subject wise events
# events  wise events
# """

#     ,"faculty_subjects": """
#     faculty subjects teaching assignments subject allocation faculty allocation

# subjects taught by faculty who teaches a subject
# faculty wise subject allocation subject wise faculty

# semester teaching subjects this semester teaching
# subjects offered in semester with faculty

# department wise teaching assignments department teaching subjects

# faculty workload teaching load per faculty
# timetable generation teaching schedule class allocation

# """
#     ,"departments": """
#         academic departments departments branch branches academic units

# cse ece mechanical civil it electrical electronics computer science
# department names department codes department short codes aliases

# list of departments how many departments
# department wise data department wise information

# department faculty department subjects department semesters
# department events department activities

# university departments college departments

#     """
#     ,"files": """
# files documents uploads uploaded files file metadata document metadata

# who uploaded a file files uploaded by user
# recently uploaded files file owner ownership

# document source source file original file
# files ingested documents ingested

# file access access level access control permissions
# files accessible by role admin faculty files

# events generated from file derived from file
# vector chunks from file document provenance

# """
#     ,"semesters": """
# semesters academic semesters academic term academic terms

# semester numbers semester 1 semester 2 semester 3 semester 4
# semester 5 semester 6 semester 7 semester 8

# department semesters semesters by department
# how many semesters department has
# list semesters for department

# semester wise subjects subjects in a semester
# semester wise faculty teaching assignments
# semester wise events events for a semester

# academic structure program structure course structure

# """
#     ,"subjects": """
# subjects courses academic subjects courses offered curriculum course catalog

# subjects offered by department department subjects
# subjects in a semester semester wise subjects

# course codes subject codes course names
# credit structure course credits

# which faculty teaches a subject subject faculty mapping
# subjects taught by faculty

# subjects related to events subject wise events

# timetable planning course planning semester course structure

# """
#     ,"users": """
# users user accounts system users

# faculty users admin users administrators
# users by role find users by role

# user access access level authorization permissions
# role based access control

# faculty members teaching faculty research faculty
# projects owned by faculty subjects taught by faculty

# files uploaded by user file owner ownership

# list users user profiles user details

# """
# }

system_user = User(
    id='a099ca49-8acd-43d8-80a4-efddcb0d8fd1', 
    username='system', 
    role='admin', 
    access_level=1
)