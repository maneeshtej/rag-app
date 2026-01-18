generate_rules:list[dict] = [
    {
    "name": "teacher_subject",
    "type": "generate",
    "priority": 0,

    "content": """
Trigger when:
- the query asks for subjects handled, taught, or taken by a teacher
- a teacher entity is present

Primary focus:
- subject

Include tables and columns:
- subjects: ["subject_name", "subject_code"]
- teachers: ["name", "email"]
    """,

    "embedding_text": """
subjects handled by teacher
subjects taught by teacher
subjects taken by teacher
subjects assigned to teacher
subjects for teacher

what subjects does the teacher teach
which subjects does the teacher handle
courses taught by faculty
courses handled by instructor
courses taught by professor
papers taught by lecturer

list subjects taught by teacher
show subjects handled by teacher
find subjects for teacher
teacher subject list

teacher teaches subject
teacher handling subject
faculty teaching subject
instructor teaching course
professor teaching course

what does teacher teach
what courses does faculty teach
what papers does lecturer teach

teaching subjects
teaching courses
teaching papers

list all the subjects handled by 
list all the subjects taught by
        """
    }
    ,
    {
    "name": "teacher_classes",
    "type": "generate",
    "priority": 0,

    "content": """
Trigger when:
- the query asks for classes handled, taught, or conducted by a teacher
- a teacher entity is present

Primary focus:
- class

Include columns:
- classes: ["class_name", "day_of_week", "start_time", "end_time", "type", "room", "label", "notes"]
- teachers: ["name", "email"]
    """,

    "embedding_text": """
classes handled by teacher
classes taught by teacher
classes conducted by teacher
classes assigned to teacher
classes for teacher

what classes does the teacher handle
which classes does the teacher teach
teacher class list
teacher schedule

list classes taught by teacher
show classes handled by faculty
find classes for instructor
classes taken by professor

teacher teaching class
teacher conducting class
faculty handling class
instructor taking class
professor teaching class

teacher timetable
teacher schedule
class schedule for teacher
teacher daily classes
teacher weekly classes

when does teacher teach
what time does teacher teach

        """
}
,
{
    "name": "teacher_class_subject",
    "type": "generate",
    "priority": 0,

    "content": """
Trigger when:
- the query involves a teacher entity
- and references classes, subjects, or teaching activity together
- examples include:
  - classes and subjects handled by a teacher
  - what a teacher teaches and when
  - teacher schedule with subjects

Primary focus:
- teaching context (teacher + class + subject)

Include columns:
- teachers: ["name", "email"]
- subjects: ["subject_name", "subject_code"]
- classes: ["class_name", "day_of_week", "start_time", "end_time", "type", "room", "label", "notes"]
    """,

    "embedding_text": """
teacher classes and subjects
classes and subjects taught by teacher
teacher teaching details
teacher teaching schedule

what does teacher teach and when
what classes and subjects does teacher handle
teacher timetable with subjects
teacher schedule with subjects

classes taught by teacher with subject
subjects taught in teacher classes
teacher subject class mapping
teaching details for teacher

faculty teaching schedule
faculty classes and subjects
instructor teaching timetable
professor teaching schedule

teacher teaching activity
teacher academic workload
teacher teaching overview

        """
}
,
{
    "name": "class_subject",
    "type": "generate",
    "priority": 0,

    "content": """
Trigger when:
- the query asks about subjects related to a class
- a class reference is present

Primary focus:
- subject

Include columns:
- subjects: ["subject_name", "subject_code"]
- classes: ["class_name", "day_of_week", "start_time", "end_time", "type", "room", "label", "notes"]
    """,

    "embedding_text": """
class subject
class subjects
subjects for class
subjects related to class
subjects associated with class

what subjects are taught in a class
which subjects does a class have
what subjects belong to a class
subjects included in a class

class syllabus
class curriculum
class course structure
class academic subjects

class subject list
list subjects for class
show subjects for class
find subjects for class

subjects taught in class
subjects covered in class
subjects conducted in class

class with subjects
class and subjects
class subject relationship
class subject mapping
subjects assigned to class

academic subjects per class
subjects offered for a class

        """
}
,
{
    "name": "class",
    "type": "generate",
    "priority": 0,

    "content": """
Trigger when:
- the query asks to list or show classes
- no other entity is present

Primary focus:
- class

Include columns:
- classes: ["class_name", "day_of_week", "start_time", "end_time", "type", "room", "label", "notes"]

    """,

    "embedding_text": """
class
classes
class list
list classes
show classes
all classes
available classes

what classes are there
which classes are available
show all classes
list all classes

class schedule
class timetable
class timings
class time table

class details
class information
class records

scheduled classes
academic classes
teaching sessions
lecture sessions
lab sessions
tutorial sessions

day wise classes
daily classes
weekly classes

class overview
class summary

        """
}
,
{
    "name": "teacher",
    "type": "generate",
    "priority": 0,

    "content": """
Trigger when:
- the query asks to list or show teachers
- no other entity is present

Primary focus:
- teacher

Include columns:
- teachers: ["name", "email"]

    """,

    "embedding_text": """
teacher
teachers
faculty
faculty members
teaching staff
academic staff

list teachers
show teachers
all teachers
available teachers

who are the teachers
who are the faculty members
show teaching staff
list faculty

teacher details
teacher information
teacher records
faculty information

professor
lecturer
instructor
teaching personnel

academic teachers
institution teachers
staff overview
teacher directory

        """
}
,
{
    "name": "subject",
    "type": "generate",
    "priority": 0,

    "content": """
Trigger when:
- the query asks to list or show subjects
- no other entity is present

Primary focus:
- subject

Include columns:
- subjects: ["subject_name", "subject_code"]

    """,

    "embedding_text": """
subject
subjects
academic subject
academic subjects
course
courses
paper
papers

list subjects
show subjects
all subjects
available subjects
subjects offered
courses offered

what subjects are there
which subjects are available
show all subjects
list all courses

subject details
subject information
subject records
course information

subject list
course list
curriculum subjects
academic offerings

subject directory
course directory
subject overview
        """
}
]