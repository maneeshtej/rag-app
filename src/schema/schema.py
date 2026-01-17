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

    Purpose:
    SUBJECTS stores canonical academic subject identities
    that are part of an institution’s curriculum.

    This table represents subjects such as
    Data Structures, Operating Systems, DBMS, Mathematics, etc.
    It does NOT represent teaching assignments, schedules, or faculty involvement.

    Table schema:
    - id: unique subject identifier (UUID)
    - subject_code: official subject or course code
    - subject_name: full human-readable subject name

    Semantics:
    - Each row represents exactly one academic subject
    - subject_code uniquely identifies a subject within an institution
    - subject_name is descriptive and not guaranteed to be unique

    Identity & resolution:
    - Subjects may be resolved using subject_code when available
    - Otherwise, subject_name may be used as a fallback identifier
    - No inference beyond identity resolution is permitted

    Non-goals / exclusions:
    - SUBJECTS does NOT store teacher information
    - SUBJECTS does NOT store class or timetable information
    - SUBJECTS does NOT encode teaching relationships

    All relationships involving subjects
    (e.g. classes, teachers, events)
    are defined and enforced outside this table
    via explicit relationship rules.

    """,

    "embedding_text": """
    subjects table
    academic subject
    academic course
    course subject
    curriculum subject

    list of subjects
    available subjects
    subjects offered
    subjects in curriculum
    academic courses offered

    subject name
    course name
    subject title
    course title

    subject code
    course code
    academic code
    course identifier

    data structures
    operating systems
    dbms
    database management systems
    computer networks
    mathematics
    physics
    chemistry
    artificial intelligence
    machine learning
    software engineering

    undergraduate subjects
    postgraduate subjects
    core subjects
    elective subjects

    subject details
    subject information
    subject record

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

    Purpose:
    TEACHERS stores canonical identity information
    for teaching staff within the institution.

    This table represents individual teachers such as
    faculty members, instructors, professors, or lecturers.
    It does NOT represent teaching assignments, schedules,
    subjects taught, or class involvement.

    Table schema:
    - id: unique teacher identifier (UUID)
    - name: full human-readable name of the teacher
    - email: official or known email address (nullable)

    Semantics:
    - Each row represents exactly one teacher
    - name is the primary human identifier
    - email, when present, uniquely identifies a teacher

    Identity & resolution:
    - Teachers may be resolved using email when available
    - Otherwise, name may be used as a fallback identifier
    - No inference of designation, department, role, or experience is permitted

    Non-goals / exclusions:
    - TEACHERS does NOT encode subject assignments
    - TEACHERS does NOT encode class schedules
    - TEACHERS does NOT encode teaching relationships

    All relationships involving teachers
    (e.g. subjects taught, classes handled)
    are defined and enforced outside this table
    via explicit relationship and join rules.

    """,

    "embedding_text": """
      teachers table
      teacher
      teachers
      faculty
      faculty member
      instructor
      course instructor
      professor
      lecturer
      teaching staff
      staff member

      teacher name
      faculty name
      instructor name
      professor name
      lecturer name

      teacher email
      faculty email
      instructor email
      professor email

      list teachers
      show teachers
      find teacher
      search teacher
      search faculty member
      show instructors
      show professors

      teacher details
      faculty details
      teacher information
      faculty profile
      professor information

      who is the teacher
      who is the instructor
      who is the professor
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

    Purpose:
    CLASSES stores scheduled class session entries
    that occur at a specific time and day.

    This table represents individual timetable sessions
    (e.g. lectures, labs, tutorials),
    not abstract academic groups, batches, or grade levels.

    Table schema:
    - id: unique class session identifier (UUID)
    - class_name: name or identifier of the class (e.g. "10A", "CS-3", "B.Tech CSE")
    - day_of_week: day on which the class occurs (e.g. Monday, Tuesday)
    - start_time: class start time
    - end_time: class end time
    - type: class type (e.g. Lecture, Lab, Tutorial)
    - room: room or location (nullable)
    - label: optional short label for the class
    - notes: additional remarks (nullable)

    Semantics:
    - Each row represents exactly one scheduled class session
    - A class session is uniquely identified by its name, day, and time window
    - This table is time-bound and event-like in nature

    Identity & resolution:
    - Class sessions may be identified using class_name,
      day_of_week, start_time, and end_time in combination
    - No collapsing or merging of multiple sessions is permitted

    Non-goals / exclusions:
    - CLASSES does NOT encode teachers assigned to the class
    - CLASSES does NOT encode subjects taught in the class
    - CLASSES does NOT encode academic groups or student batches

    All relationships involving classes
    (e.g. teachers, subjects, schedules)
    are defined and enforced outside this table
    via explicit relationship and join rules.

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

    what classes are scheduled
    classes today
    classes on monday
    class schedule for today

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

    Purpose:
    CLASS_SUBJECTS encodes the relationship between
    scheduled class sessions and academic subjects.

    This table exists ONLY to support relational joins.
    It does NOT represent standalone domain entities
    and MUST NOT be queried as a primary data source.

    Table schema:
    - id: unique relationship identifier (UUID)
    - class_id: references classes.id
    - subject_id: references subjects.id

    Semantics:
    - Each row links exactly one class session to one subject
    - This is a pure relationship (join) table
    - No descriptive, temporal, or identity data is stored here

    Identity & resolution:
    - Entries MUST be referenced only via existing class_id and subject_id
    - This table MUST NOT be resolved using text or embeddings
    - No inference or lookup is permitted at this level

    Usage constraints (STRICT):
    - CLASS_SUBJECTS MUST NOT be selected from directly
    - CLASS_SUBJECTS MUST be used only as part of an explicit join path
    - Filtering logic MUST be applied on parent tables
      (e.g. CLASSES or SUBJECTS), not on this table

    All valid join paths involving this table
    are defined and enforced via explicit schema join rules.

    """,

    "embedding_text": """
    class_subjects table
    class to subject mapping
    class subject relationship
    class subject link
    timetable subject association

    class_id subject_id mapping
    relationship table
    join table

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

    Purpose:
    CLASS_TEACHERS encodes the relationship between
    teachers and scheduled class sessions.

    This table exists ONLY to support relational joins.
    It does NOT represent standalone domain entities
    and MUST NOT be queried as a primary data source.

    Table schema:
    - id: unique relationship identifier (UUID)
    - class_id: references classes.id
    - teacher_id: references teachers.id
    - role: optional role of the teacher in the class
      (e.g. "Instructor", "Lab Assistant", "Co-Teacher")

    Semantics:
    - Each row links exactly one teacher to one class session
    - Multiple teachers may be assigned to the same class
    - A teacher may appear in many class sessions
    - This is a pure relationship (join) table

    Identity & resolution:
    - Entries MUST be referenced only via existing class_id and teacher_id
    - This table MUST NOT be resolved using text or embeddings
    - No inference or lookup is permitted at this level

    Usage constraints (STRICT):
    - CLASS_TEACHERS MUST NOT be selected from directly
    - CLASS_TEACHERS MUST be used only as part of an explicit join path
    - Filtering logic MUST be applied on parent tables
      (e.g. CLASSES or TEACHERS), not on this table

    All valid join paths involving this table
    are defined and enforced via explicit schema join rules.

    """,

    "embedding_text": """
    class_teachers table
    class to teacher mapping
    teacher class relationship
    class teacher link

    class_id teacher_id mapping
    relationship table
    join table

    teacher role in class
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