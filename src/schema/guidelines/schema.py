schema_rules:list[dict] = [
    {
    "name": "subjects",
    "type": "schema",
    "priority": 4,
    "active": True,

    "content": """
    This guidance defines the subjects table.

    Table meaning:
    The subjects table stores academic subjects offered by an institution.
    Each row represents one subject in the curriculum.

    Columns:
    - subject_code: string
    Official subject or course code used by the institution.
    - subject_name: string
    Human-readable name of the subject.

    Notes:
    - This table represents subject identity only.
    - It does not encode teaching, scheduling, or enrollment information.

    """,

    "embedding_text": """
   subjects
subject
academic subject
academic course
course
paper
curriculum subject

list subjects
show subjects
available subjects
subjects offered
courses offered
subjects in curriculum
academic courses available

what subjects are there
what courses are offered
which subjects are available
show all subjects
list all courses
list all papers

subject name
course name
paper name
subject title
course title

subject code
course code
paper code
academic code

get subject name
get subject code
retrieve subject details
subject information
course information

data structures
operating systems
dbms
database management systems
computer networks
artificial intelligence
machine learning
software engineering
mathematics
physics
chemistry

undergraduate subjects
postgraduate subjects
core subjects
elective subjects

does subject exist
is this subject offered
check subject availability
find subject
search subject
search course

subject list
course list
curriculum list
academic offerings

    """
},
{
    "name": "teachers",
    "type": "schema",
    "priority": 4,
    "active": True,

    "content": """
    This defines the teachers table.

    Table meaning:
    The teachers table stores information about teaching staff
    within an institution.

    Columns:
    - name: string
      Full human-readable name of the teacher.
    - email: string (nullable)
      Official or known email address of the teacher.

    Notes:
    - Each row represents one teacher.
    - This table stores identity information only.
    """,

    "embedding_text": """
        teachers
teacher
faculty
faculty member
instructor
professor
lecturer
teaching staff
staff member

list teachers
show teachers
all teachers
available teachers
faculty list
staff list

who are the teachers
who are the faculty members
show teaching staff
list instructors
list professors
list lecturers

teacher name
faculty name
instructor name
professor name
lecturer name

teacher email
faculty email
instructor email
professor email
lecturer email
staff email

find teacher
search teacher
lookup teacher
get teacher details
teacher information
faculty information
teacher profile

does teacher exist
is this teacher present
check teacher availability
find faculty member

who is the teacher
who is the instructor
who is the professor
who is the lecturer

teacher record
faculty record
staff record

"""
}
,
{
    "name": "classes",
    "type": "schema",
    "priority": 4,
    "active": True,

    "content": """
    This defines the classes table.

    Table meaning:
    The classes table stores scheduled class session records
    that occur on a specific day and time.

    Columns:
    - class_name: string
      Name or identifier of the class.
    - day_of_week: string
      Day on which the class session occurs.
    - start_time: time
      Start time of the class session.
    - end_time: time
      End time of the class session.
    - type: string
      Type of class (e.g. Lecture, Lab, Tutorial).
    - room: string (nullable)
      Room or location of the class.
    - label: string (nullable)
      Optional short label for the class.
    - notes: string (nullable)
      Additional remarks for the class session.
    """,

    "embedding_text": """
classes
class
class session
scheduled class
timetable entry
lecture
lab
tutorial

list classes
show classes
all classes
class schedule
timetable
daily schedule
weekly schedule

what classes are there
which classes are scheduled
show today classes
show classes on monday
show classes tomorrow

class name
class identifier
section name
batch name
group name

day of week
class day
weekday
monday
tuesday
wednesday
thursday
friday
saturday

class time
start time
end time
class timing
class duration

lecture class
lab session
tutorial session
class type

class room
room number
location
classroom
lab room

class label
class notes
remarks
additional notes

find class
search class
lookup class
class details
class information

class list
timetable list
schedule list
"""
}

]