from src.models.user import User

SQL_SCHEMA_EMBEDDINGS = [
    {
        "name": "events",
        "content": "", 
        "schema": {
            "description": "Academic and administrative events with time windows",
            "columns": {
                "id": "unique event identifier",
                "title": "event title",
                "event_type": "type of event such as exam holiday notice assignment",
                "start_time": "event start date and time",
                "end_time": "event end date and time",
                "department_id": "department related to the event",
                "subject_id": "subject related to the event",
                "file_id": "source document for the event",
                "metadata": "additional event information",
            },
            "joins": {
                "department_id": "departments.id",
                "subject_id": "subjects.id",
                "file_id": "files.id",
            },
            "entity_resolve_columns": ["title", "event_type"]
        },
        "related_tables": [
            "departments",
            "subjects",
            "files",
        ],
        "embedding_text": """
            academic events administrative events university events college events

            exam schedule exam dates mid exam end exam internal exam
            assignment deadlines submissions due dates
            holiday list public holidays academic holidays
            notices announcements circulars schedule changes

            academic calendar calendar timetable
            upcoming events events this week events this month events 
            events between dates important events

            department events department wise events
            subject events subject wise events
""",      # placeholder (what you actually embed)
    },

    {
    "name": "faculty_subjects",
    "content": "",
    "schema": {
        "description": "Teaching assignments mapping faculty to subjects",
        "columns": {
            "id": "teaching assignment identifier",
            "faculty_id": "faculty teaching the subject",
            "subject_id": "subject being taught",
            "department_id": "department offering the subject",
            "created_at": "record creation time"
        },
        "joins": {
            "faculty_id": "faculty.id",
            "subject_id": "subjects.id",
            "department_id": "departments.id"
        },
        "entity_resolve_columns": []
    },
    "related_tables": [
        "faculty",
        "subjects",
        "departments"
    ],
    "embedding_text": """
        faculty subjects teaching assignments subject allocation faculty allocation

        subjects taught by faculty who teaches a subject
        faculty wise subject allocation subject wise faculty

        department wise teaching assignments department teaching subjects

        faculty workload teaching load per faculty
        timetable generation teaching schedule class allocation
    """
}
,

    {
        "name": "departments",
        "content": "",
        "schema": {
            "description": "Academic departments or branches",
            "columns": {
                "id": "department identifier",
                "name": "full department name",
                "short_code": "abbreviated department code",
                "aliases": "alternative department names",
            },
            "joins": {
                "id": [
                    "events.department_id",
                    "faculty_subjects.department_id",
                    "subjects.department_id",
                ],
            },
            "entity_resolve_columns": ["name", "short_code", "aliases"]
        },
        "related_tables": [
            "events",
            "faculty_subjects",
            "subjects",
        ],
        "embedding_text": """
        academic departments departments branch branches academic units

        cse ece mechanical civil it electrical electronics computer science
        department names department codes department short codes aliases

        list of departments how many departments
        department wise data department wise information

        department faculty department subjects department 
        department events department activities

        university departments college departments
""",
    },

    

    {
        "name": "subjects",
        "content": "",
        "schema": {
            "description": "Academic subjects or courses in a curriculum",
            "columns": {
                "id": "subject identifier",
                "code": "official subject code",
                "name": "subject name",
                "department_id": "department offering the subject",
                "credits": "credit structure of the subject",
            },
            "joins": {
                "department_id": "departments.id",
                "id": [
                    "events.subject_id",
                    "faculty_subjects.subject_id",
                ],
            },
            "entity_resolve_columns": ["code", "name"]
        },
        "related_tables": [
            "departments",
            "events",
            "faculty_subjects",
        ],
        "embedding_text": """
        subjects courses academic subjects courses offered curriculum course catalog

        subjects offered by department department subjects

        course codes subject codes course names
        credit structure course credits

        which faculty teaches a subject subject faculty mapping
        subjects taught by faculty

        subjects related to events subject wise events
""",
    },

    {
    "name": "faculty",
    "content": "",
    "schema": {
        "description": "Academic faculty members of the institution",
        "columns": {
            "id": "faculty identifier",
            "name": "full name of faculty member",
            "designation": "academic designation",
            "email": "official email address",
            "contact_no": "contact number",
            "joining_date": "date of joining",
            "experience_years": "total teaching or industry experience",
            "created_at": "record creation time",
            "updated_at": "last record update time"
        },
        "joins": {
            "id": [
                "faculty_subjects.faculty_id"
            ]
        },
        "entity_resolve_columns": ["name", "email", "designation"]
    },
    "related_tables": [
        "faculty_subjects"
    ],

    "embedding_text": """
        faculty academic staff teaching staff professors lecturers

        faculty profiles academic background experience qualifications

        faculty subjects taught teaching assignments courses handled

        faculty research interests achievements sponsored projects

        department faculty academic department teaching staff

        list faculty find professors lecturers instructors
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