from src.models.user import User

SQL_SCHEMA_EMBEDDINGS = [
    {
        "name": "events",
        "content": "",            # placeholder (human-readable later)
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
                "semester_id": "semester related to the event",
                "file_id": "source document for the event",
                "metadata": "additional event information",
            },
            "joins": {
                "department_id": "departments.id",
                "subject_id": "subjects.id",
                "semester_id": "semesters.id",
                "file_id": "files.id",
            },
            "entity_resolve_columns": ["title", "event_type"]
        },
        "related_tables": [
            "departments",
            "subjects",
            "semesters",
            "files",
        ],
        "embedding_text": """
            academic events administrative events university events college events

            exam schedule exam dates mid semester exam end semester exam internal exam
            assignment deadlines submissions due dates
            holiday list public holidays academic holidays
            notices announcements circulars schedule changes

            academic calendar semester calendar timetable
            upcoming events events this week events this month events this semester
            events between dates important events

            department events department wise events
            subject events subject wise events
            semester events semester wise events
""",      # placeholder (what you actually embed)
    },

    {
        "name": "faculty_projects",
        "content": "",
        "schema": {
            "description": "Research or institutional projects undertaken by faculty",
            "columns": {
                "id": "project identifier",
                "faculty_id": "faculty member leading the project",
                "title": "project title",
                "domain": "research or work domain",
                "description": "project description",
                "start_date": "project start date",
                "end_date": "project end date if completed",
                "created_at": "record creation time",
                "status": "project status ongoing completed paused",
            },
            "joins": {
                "faculty_id": "users.id",
            },
            "entity_resolve_columns": ["title", "domain"]
        },
        "related_tables": [
            "users",
        ],
        "embedding_text": """
            faculty projects faculty research projects academic projects institutional projects

            faculty research work research domains research areas
            ai projects networks projects education projects interdisciplinary research

            ongoing projects completed projects paused projects
            projects without end date active research work

            faculty wise projects projects by faculty
            principal investigator co investigator
            department research projects university research projects college research

            research output faculty achievements
            long term academic initiatives project timeline project duration
""",
    },

    {
        "name": "faculty_subjects",
        "content": "",
        "schema": {
            "description": "Teaching assignments mapping faculty to subjects per semester",
            "columns": {
                "id": "teaching assignment identifier",
                "faculty_id": "faculty teaching the subject",
                "subject_id": "subject being taught",
                "semester_id": "semester of teaching",
                "department_id": "department offering the subject",
                "created_at": "record creation time",
            },
            "joins": {
                "faculty_id": "users.id",
                "subject_id": "subjects.id",
                "semester_id": "semesters.id",
                "department_id": "departments.id",
            },
            "entity_resolve_columns": []
        },
        "related_tables": [
            "users",
            "subjects",
            "semesters",
            "departments",
        ],
        "embedding_text": """
         faculty subjects teaching assignments subject allocation faculty allocation

        subjects taught by faculty who teaches a subject
        faculty wise subject allocation subject wise faculty

        semester teaching subjects this semester teaching
        subjects offered in semester with faculty

        department wise teaching assignments department teaching subjects

        faculty workload teaching load per faculty
        timetable generation teaching schedule class allocation
""",
    },

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
                    "semesters.department_id",
                    "subjects.department_id",
                ],
            },
            "entity_resolve_columns": ["name", "short_code", "aliases"]
        },
        "related_tables": [
            "events",
            "faculty_subjects",
            "semesters",
            "subjects",
        ],
        "embedding_text": """
        academic departments departments branch branches academic units

        cse ece mechanical civil it electrical electronics computer science
        department names department codes department short codes aliases

        list of departments how many departments
        department wise data department wise information

        department faculty department subjects department semesters
        department events department activities

        university departments college departments
""",
    },

    {
        "name": "files",
        "content": "",
        "schema": {
            "description": "Metadata for uploaded or ingested documents",
            "columns": {
                "id": "file identifier",
                "owner_id": "user who uploaded the file",
                "role": "role of the uploader",
                "source": "original file name or source",
                "access_level": "file access control level",
                "created_at": "file upload time",
            },
            "joins": {
                "owner_id": "users.id",
                "id": [
                    "events.file_id",
                    "vector_chunks.file_id",
                ],
            },
            "entity_resolve_columns": ["role", "source"]
        },
        "related_tables": [
            "users",
            "events",
        ],
        "embedding_text": """
        files documents uploads uploaded files file metadata document metadata

        who uploaded a file files uploaded by user
        recently uploaded files file owner ownership

        document source source file original file
        files ingested documents ingested

        file access access level access control permissions
        files accessible by role admin faculty files

        events generated from file derived from file
        vector chunks from file document provenance
""",
    },

    {
        "name": "semesters",
        "content": "",
        "schema": {
            "description": "Academic semesters under a department",
            "columns": {
                "id": "semester identifier",
                "number": "semester number",
                "department_id": "department offering the semester",
            },
            "joins": {
                "department_id": "departments.id",
                "id": [
                    "events.semester_id",
                    "faculty_subjects.semester_id",
                    "subjects.semester_id",
                ],
            },
            "entity_resolve_columns": []
        },
        "related_tables": [
            "departments",
            "events",
            "faculty_subjects",
            "subjects",
        ],
        "embedding_text": """
        semesters academic semesters academic term academic terms

        semester numbers semester 1 semester 2 semester 3 semester 4
        semester 5 semester 6 semester 7 semester 8

        department semesters semesters by department
        how many semesters department has
        list semesters for department

        semester wise subjects subjects in a semester
        semester wise faculty teaching assignments
        semester wise events events for a semester

        academic structure program structure course structure
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
                "semester_id": "semester in which subject is taught",
                "credits": "credit structure of the subject",
            },
            "joins": {
                "department_id": "departments.id",
                "semester_id": "semesters.id",
                "id": [
                    "events.subject_id",
                    "faculty_subjects.subject_id",
                ],
            },
            "entity_resolve_columns": ["code", "name"]
        },
        "related_tables": [
            "departments",
            "semesters",
            "events",
            "faculty_subjects",
        ],
        "embedding_text": """
        subjects courses academic subjects courses offered curriculum course catalog

        subjects offered by department department subjects
        subjects in a semester semester wise subjects

        course codes subject codes course names
        credit structure course credits

        which faculty teaches a subject subject faculty mapping
        subjects taught by faculty

        subjects related to events subject wise events

        timetable planning course planning semester course structure
""",
    },

    {
        "name": "users",
        "content": "",
        "schema": {
            "description": "System users such as faculty and administrators",
            "columns": {
                "id": "user identifier",
                "username": "login or display name",
                "role": "user role such as faculty or admin",
                "access_level": "numeric authorization level",
                "created_at": "account creation time",
            },
            "joins": {
                "id": [
                    "faculty_projects.faculty_id",
                    "faculty_subjects.faculty_id",
                    "files.owner_id",
                ],
            },
            "entity_resolve_columns": ["username", "role"]
        },
        "related_tables": [
            "faculty_projects",
            "faculty_subjects",
            "files",
        ],
        "embedding_text": """
            users user accounts system users

            faculty users admin users administrators
            users by role find users by role

            user access access level authorization permissions
            role based access control

            faculty members teaching faculty research faculty
            projects owned by faculty subjects taught by faculty

            files uploaded by user file owner ownership

            list users user profiles user details
""",
    },
]




schema = {
    "events": """

    academic events administrative events university events college events

exam schedule exam dates mid semester exam end semester exam internal exam
assignment deadlines submissions due dates
holiday list public holidays academic holidays
notices announcements circulars schedule changes

academic calendar semester calendar timetable
upcoming events events this week events this month events this semester
events between dates important events

department events department wise events
subject events subject wise events
semester events semester wise events
"""
    ,"faculty_projects": """
    faculty projects faculty research projects academic projects institutional projects

faculty research work research domains research areas
ai projects networks projects education projects interdisciplinary research

ongoing projects completed projects paused projects
projects without end date active research work

faculty wise projects projects by faculty
principal investigator co investigator
department research projects university research projects college research

research output faculty achievements
long term academic initiatives project timeline project duration
"""
    ,"faculty_subjects": """
    faculty subjects teaching assignments subject allocation faculty allocation

subjects taught by faculty who teaches a subject
faculty wise subject allocation subject wise faculty

semester teaching subjects this semester teaching
subjects offered in semester with faculty

department wise teaching assignments department teaching subjects

faculty workload teaching load per faculty
timetable generation teaching schedule class allocation

"""
    ,"departments": """
        academic departments departments branch branches academic units

cse ece mechanical civil it electrical electronics computer science
department names department codes department short codes aliases

list of departments how many departments
department wise data department wise information

department faculty department subjects department semesters
department events department activities

university departments college departments

    """
    ,"files": """
files documents uploads uploaded files file metadata document metadata

who uploaded a file files uploaded by user
recently uploaded files file owner ownership

document source source file original file
files ingested documents ingested

file access access level access control permissions
files accessible by role admin faculty files

events generated from file derived from file
vector chunks from file document provenance

"""
    ,"semesters": """
semesters academic semesters academic term academic terms

semester numbers semester 1 semester 2 semester 3 semester 4
semester 5 semester 6 semester 7 semester 8

department semesters semesters by department
how many semesters department has
list semesters for department

semester wise subjects subjects in a semester
semester wise faculty teaching assignments
semester wise events events for a semester

academic structure program structure course structure

"""
    ,"subjects": """
subjects courses academic subjects courses offered curriculum course catalog

subjects offered by department department subjects
subjects in a semester semester wise subjects

course codes subject codes course names
credit structure course credits

which faculty teaches a subject subject faculty mapping
subjects taught by faculty

subjects related to events subject wise events

timetable planning course planning semester course structure

"""
    ,"users": """
users user accounts system users

faculty users admin users administrators
users by role find users by role

user access access level authorization permissions
role based access control

faculty members teaching faculty research faculty
projects owned by faculty subjects taught by faculty

files uploaded by user file owner ownership

list users user profiles user details

"""
}

system_user = User(
    id='a099ca49-8acd-43d8-80a4-efddcb0d8fd1', 
    username='system', 
    role='admin', 
    access_level=1
)