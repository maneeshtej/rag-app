from src.models.user import User


schema = {
"events": """
Table: events

Purpose:
Stores all academic and administrative events such as exams, holidays,
assignments, notices, schedules, and other time-bound activities.
Each row represents a single event with a defined time window.

Columns:
id (uuid, primary key) – unique identifier for the event.
title (text) – human-readable title of the event.
event_type (text) – category of the event (e.g., exam, holiday, notice, assignment).
start_time (timestamp) – event start date and time.
end_time (timestamp) – event end date and time.
department_id (uuid, nullable) – department associated with the event.
subject_id (uuid, nullable) – subject related to the event, if applicable.
semester_id (uuid, nullable) – semester associated with the event.
file_id (uuid, not null) – reference to the source file or document.
metadata (jsonb) – flexible additional information about the event.

Relationships / Joins:
events.department_id → departments.id (ON DELETE SET NULL)
events.subject_id → subjects.id (ON DELETE SET NULL)
events.semester_id → semesters.id (ON DELETE SET NULL)
events.file_id → files.id (ON DELETE CASCADE)

This table acts as a central timeline for all institution-related activities
and is commonly filtered by department, semester, subject, or event type.

Example questions:
- What events are scheduled for this semester?
- List all exam-related events.
- Events for a specific department.
- Subject-wise event timeline.
- Upcoming events between two dates.
- Events uploaded via a specific file.

Keywords:
event, events, schedule, exam, holiday, notice, academic calendar,
department-wise events, semester events, subject events, timeline
""",
"faculty_projects": """
Table: faculty_projects

Purpose:
Stores academic, research, or institutional projects undertaken by faculty members.
Each row represents a single project owned or led by a faculty member.

Columns:
id (uuid, primary key) – unique identifier for the faculty project.
faculty_id (uuid, not null) – faculty member associated with the project.
title (text) – title of the project.
domain (text, nullable) – research or work domain (e.g., AI, Networks, Education).
description (text, nullable) – detailed description of the project.
start_date (timestamp) – project start date.
end_date (timestamp, nullable) – project end or completion date.
created_at (timestamp) – record creation timestamp.
status (text, nullable) – current project status (e.g., ongoing, completed, paused).

Relationships / Joins:
faculty_projects.faculty_id → users.id

This table is used to track faculty research activity, institutional projects,
and long-term academic initiatives. It is commonly used for profiling faculty,
reporting research output, and monitoring project timelines.

Example questions:
- What projects is a faculty member currently working on?
- List all ongoing faculty projects.
- Projects by domain.
- Completed projects in the last year.
- Faculty-wise project count.
- Projects without an end date (ongoing).

Keywords:
faculty projects, research projects, academic projects, faculty research,
domain-wise projects, ongoing projects, completed projects
""",
"faculty_subjects": """
Table: faculty_subjects

Purpose:
Maps faculty members to the subjects they teach within a specific semester
and department. Each row represents a teaching assignment.

Columns:
id (uuid, primary key) – unique identifier for the faculty–subject assignment.
faculty_id (uuid, not null) – faculty member assigned to teach the subject.
subject_id (uuid, not null) – subject being taught.
semester_id (uuid, not null) – semester during which the subject is taught.
department_id (uuid, not null) – department offering the subject.
created_at (timestamp) – record creation timestamp.

Relationships / Joins:
faculty_subjects.faculty_id → users.id (ON DELETE CASCADE)
faculty_subjects.subject_id → subjects.id (ON DELETE CASCADE)
faculty_subjects.semester_id → semesters.id (ON DELETE CASCADE)
faculty_subjects.department_id → departments.id (ON DELETE CASCADE)

This table acts as a junction (many-to-many) table connecting faculty,
subjects, semesters, and departments. It is central to timetable generation,
faculty workload analysis, and subject allocation management.

Example questions:
- Which subjects does a faculty member teach this semester?
- Who teaches a specific subject?
- Faculty-wise subject allocation.
- Department-wise teaching assignments.
- Subjects offered in a semester with assigned faculty.
- Teaching load per faculty member.

Keywords:
faculty subjects, teaching assignments, faculty allocation,
subject assignment, semester teaching, department-wise teaching
""",
"departments": """
Table: departments

Purpose:
Stores academic departments within the institution.
Each department represents an academic unit such as CSE, ECE, Mechanical, etc.

Columns:
id (uuid, primary key) – unique identifier for a department.
name (text, not null) – full name of the department.
short_code (text, nullable) – abbreviated code for the department (e.g., CSE, ECE).
aliases (text, nullable) – alternative names or abbreviations for the department.

Relationships / Joins:
departments.id is referenced by:
- events.department_id (ON DELETE SET NULL)
- faculty_subjects.department_id (ON DELETE CASCADE)
- semesters.department_id
- subjects.department_id (ON DELETE CASCADE)

This table serves as a core parent entity used across the system
to group subjects, semesters, faculty assignments, and events by department.

Example questions:
- How many departments are there?
- List all departments.
- Department-wise faculty allocation.
- Subjects offered by each department.
- Semesters available per department.
- Events conducted by each department.

Keywords:
department, departments, branch, academic unit,
CSE, ECE, ME, department-wise data
""",
"files": """
Table: files

Purpose:
Stores metadata about uploaded or ingested files in the system.
Each file acts as a source document for events, vector embeddings,
and other derived records.

Columns:
id (uuid, primary key) – unique identifier for the file.
owner_id (uuid, not null) – user who uploaded or owns the file.
role (text, not null) – role of the owner at upload time (e.g., admin, faculty).
source (text, nullable) – original file source or filename.
access_level (integer, not null) – access control level for the file.
created_at (timestamp) – file creation timestamp.

Relationships / Joins:
files.owner_id → users.id
files.id is referenced by:
- events.file_id (ON DELETE CASCADE)
- vector_chunks.file_id (ON DELETE CASCADE)

This table serves as the backbone for document-level access control
and provenance tracking. Deleting a file cascades to all derived
events and vector chunks originating from that file.

Example questions:
- Who uploaded a specific file?
- List files uploaded by a user.
- Files accessible at a given access level.
- Events generated from a file.
- Vector chunks associated with a file.
- Recently uploaded files.

Keywords:
files, documents, uploads, file metadata,
access control, ownership, document source
""",
"semesters": """
Table: semesters

Purpose:
Represents academic semesters within a specific department.
Each row defines a semester number (e.g., 1–8) under a department.

Columns:
id (uuid, primary key) – unique identifier for the semester.
number (integer, not null) – semester number (e.g., 1, 2, 3).
department_id (uuid, not null) – department to which the semester belongs.

Relationships / Joins:
semesters.department_id → departments.id
semesters.id is referenced by:
- events.semester_id (ON DELETE SET NULL)
- faculty_subjects.semester_id (ON DELETE CASCADE)
- subjects.semester_id (ON DELETE CASCADE)

This table provides academic structure and is commonly used
to organize subjects, events, and faculty assignments
by department and semester.

Example questions:
- How many semesters does a department have?
- List semesters for a department.
- Subjects offered in a specific semester.
- Faculty teaching assignments per semester.
- Events scheduled for a semester.

Keywords:
semester, semesters, academic term,
department semesters, semester-wise data
""",
"subjects": """
Table: subjects

Purpose:
Stores academic subjects offered by a department in a specific semester.
Each subject represents a course taught as part of the curriculum.

Columns:
id (uuid, primary key) – unique identifier for the subject.
code (text, not null) – official subject code (e.g., CS101).
name (text, not null) – full name of the subject.
department_id (uuid, not null) – department offering the subject.
semester_id (uuid, not null) – semester in which the subject is taught.
credits (text, nullable) – credit structure of the subject.

Relationships / Joins:
subjects.department_id → departments.id (ON DELETE CASCADE)
subjects.semester_id → semesters.id (ON DELETE CASCADE)
subjects.id is referenced by:
- events.subject_id (ON DELETE SET NULL)
- faculty_subjects.subject_id (ON DELETE CASCADE)

This table defines the academic curriculum and is central to
timetabling, faculty assignment, and semester-wise course planning.

Example questions:
- List all subjects for a semester.
- Subjects offered by a department.
- Which faculty teaches a subject?
- Credit structure of a subject.
- Subjects associated with academic events.
- Semester-wise subject list.

Keywords:
subjects, courses, curriculum,
department subjects, semester subjects, course catalog
""",
"users": """
Table: users

Purpose:
Stores system users such as administrators, faculty members, and other roles.
Each user represents an authenticated actor in the system with defined access privileges.

Columns:
id (uuid, primary key) – unique identifier for the user.
username (text, not null, unique) – unique login or identifier for the user.
role (text, not null) – role assigned to the user (e.g., admin, faculty).
access_level (integer, not null) – numeric access control level for authorization.
created_at (timestamp) – user account creation timestamp.

Relationships / Joins:
users.id is referenced by:
- faculty_projects.faculty_id
- faculty_subjects.faculty_id (ON DELETE CASCADE)
- files.owner_id

This table acts as the root identity and authorization entity.
It is used for access control, ownership tracking, and role-based filtering
across files, events, faculty assignments, and projects.

Example questions:
- List all users.
- Find users by role.
- Files uploaded by a user.
- Subjects taught by a faculty member.
- Projects owned by a faculty member.
- Users with a specific access level.

Keywords:
users, user accounts, faculty, admins,
roles, access control, authorization
""",
}

bare_schema = {
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