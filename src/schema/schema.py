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
        - department-wise or subject-wise scheduled activities
        - upcoming, ongoing, or past events bounded by start_time and end_time

        Columns:
        - id: unique identifier of the event
        - title: name or heading of the event
        - event_type: category such as exam, holiday, assignment, notice, announcement
        - start_time: datetime when the event starts
        - end_time: datetime when the event ends
        - department_id: link to departments table
        - subject_id: link to subjects table
        - file_id: source document reference
        - metadata: additional structured or unstructured details

        Joins:
        - events.department_id → departments.id
        - events.subject_id → subjects.id
        - events.file_id → files.id

        Filtering rules:
        - Use start_time and end_time for date range queries
        - Filter by department_id for department-specific events
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

        department wise events department specific notices
        subject wise events subject related exams assignments
        events related to a department events related to a subject

        when is the exam
        what events are coming up
        show upcoming academic events
        list holidays this month
        what assignments are due
        events for a specific department
        events for a specific subject
        """
    }
    ,
    {
        "name": "faculty_subjects",
        "type": "schema_guidance",
        "priority": 3,
        "active": True,

        "content": """
        This guidance defines the FACULTY_SUBJECTS table.

        Use this table when the user asks about which faculty teaches which subject, or about teaching assignments.

        FACULTY_SUBJECTS represents the mapping between faculty members and the subjects they teach.

        Each row corresponds to one teaching assignment.

        Columns:
        - id: unique teaching assignment identifier
        - faculty_id: reference to the faculty member
        - subject_id: reference to the subject being taught
        - department_id: department offering the subject
        - created_at: timestamp when the assignment was created

        Joins:
        - faculty_subjects.faculty_id → faculty.id
        - faculty_subjects.subject_id → subjects.id
        - faculty_subjects.department_id → departments.id

        Usage rules:
        - Use faculty_id to fetch subjects taught by a faculty member
        - Use subject_id to fetch faculty teaching a subject
        - Use department_id for department-wise teaching assignments
        - This table does NOT contain timetable or class session timing information
        """,

            "embedding_text": """
        faculty subjects table teaching assignments faculty subject mapping

        who teaches which subject
        subjects taught by a faculty
        faculty teaching a subject
        faculty wise subject allocation
        subject wise faculty allocation

        department wise teaching assignments
        department faculty subject mapping
        subjects offered by a department and faculty

        faculty workload teaching load
        number of subjects per faculty
        faculty allocation for subjects

        teaching assignment data
        faculty subject relationship
        which faculty handles a subject
        """
    }
    ,
    {
        "name": "departments",
        "type": "schema_guidance",
        "priority": 4,
        "active": True,

        "content": """
        This guidance defines the DEPARTMENTS table.

        Use this table when the user asks about academic departments, branches, or organizational units.

        DEPARTMENTS represents academic units such as CSE, ECE, Mechanical, Civil, IT, etc.

        Columns:
        - id: unique department identifier
        - name: full department name
        - short_code: abbreviated department code
        - aliases: alternative or informal names for the department

        Joins:
        - departments.id → events.department_id
        - departments.id → faculty_subjects.department_id
        - departments.id → subjects.department_id

        Usage rules:
        - Resolve departments using name, short_code, or aliases
        - Use department id as the root filter for department-wise queries
        - Departments act as a parent entity for subjects, faculty assignments, and events
        """,

            "embedding_text": """
        departments table academic departments branches academic units

        cse ece it civil mechanical electrical electronics computer science
        department names department codes short codes aliases

        list of departments
        how many departments
        show all departments
        department information

        department wise data
        department wise subjects
        department wise faculty
        department wise events
        department activities

        college departments university departments
        branch wise information
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

        Use this table when the user asks about academic subjects or courses offered as part of a curriculum.

        SUBJECTS represents individual courses such as Data Structures, Operating Systems, DBMS, etc.

        Columns:
        - id: unique subject identifier
        - code: official subject or course code
        - name: subject name
        - department_id: department offering the subject
        - credits: credit structure of the subject

        Joins:
        - subjects.department_id → departments.id
        - subjects.id → events.subject_id
        - subjects.id → faculty_subjects.subject_id

        Usage rules:
        - Resolve subjects using subject code or subject name
        - Use department_id for department-wise subject queries
        - Use subject id to fetch related faculty assignments or subject-specific events
        - SUBJECTS does not store faculty or event timing information directly
        """,

            "embedding_text": """
        subjects table academic subjects courses course catalog curriculum

        course code subject code
        course name subject name
        credits credit structure credit count

        subjects offered by department
        department wise subjects
        courses offered by a department

        which faculty teaches a subject
        subject faculty mapping
        faculty for a subject

        subject wise events
        events related to a subject
        exams assignments notices for a subject

        list of subjects
        show all subjects
        """
    }
    ,
    {
        "name": "faculty",
        "type": "schema_guidance",
        "priority": 4,
        "active": True,

        "content": """
        This guidance defines the FACULTY table.

        Use this table when the user asks about academic faculty members, instructors, professors, or teaching staff.

        FACULTY represents individual academic staff profiles of the institution.

        Columns:
        - id: unique faculty identifier
        - name: full name of the faculty member
        - designation: academic designation or role
        - email: official email address
        - contact_no: contact phone number
        - joining_date: date when the faculty joined the institution
        - experience_years: total academic or industry experience
        - created_at: record creation timestamp
        - updated_at: record last update timestamp

        Joins:
        - faculty.id → faculty_subjects.faculty_id

        Usage rules:
        - Resolve faculty entities using name, email, or designation
        - Use faculty id to fetch subjects taught via faculty_subjects
        - FACULTY does not directly store subject, department, or event data
        """,

            "embedding_text": """
        faculty table academic faculty teaching staff professors lecturers instructors

        faculty profile faculty details
        faculty name designation email contact
        faculty experience years joining date

        which subjects does a faculty teach
        subjects taught by faculty
        faculty subject mapping

        list faculty
        find faculty member
        search professor lecturer instructor

        department faculty
        academic staff information
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