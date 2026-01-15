import io
import json
from uuid import UUID
from langchain_core.messages import HumanMessage
import base64
from PIL import Image
import io
import base64
import mimetypes
import re

test_output = {'class_details': {'class_name': 'VII(A)',
  'department': 'Computer Science & Engineering',
  'academic_year': '2025-26',
  'semester': 'ODD',
  'default_room': '236B'},
 'subjects': {'22CS71': 'High Performance Computing',
  '22CS72': 'Cyber Security',
  '22CS73': 'Green Computing',
  '22CS74': 'Cloud Computing',
  '22CS75': 'Full Stack Development',
  '22CS76': 'High Performance Computing Lab',
  '22CS771': 'Deep Learning with Python',
  '22CS772': 'Internet Of Things',
  '22CS773': 'Cyber Laws And Ethics',
  '22CS774': 'Blockchain Technology',
  '22CSP78': 'Major Project Phase 1'},
 'teachers': {'Dr. Jayashree': {'name': 'Dr. Jayashree',
   'email': 'jayashree.cse@nnmit.ac.in'},
  'Dr. Janardhana D R': {'name': 'Dr. Janardhana D R',
   'email': 'janardhana.dr@nnmit.ac.in'},
  'Dr. Saroja Devi H': {'name': 'Dr. Saroja Devi H',
   'email': 'sarojadevi.h@nnmit.ac.in'},
  'Ms. Kavitha K K': {'name': 'Ms. Kavitha K K',
   'email': 'kavitha.kk@nnmit.ac.in'},
  'Dr. P Ramesh Naidu': {'name': 'Dr. P Ramesh Naidu',
   'email': 'ramesh.naidu@nnmit.ac.in'},
  'Dr. N Jayasree': {'name': 'Dr. N Jayasree',
   'email': 'njayasree.cse@nnmit.ac.in'},
  'Dr. Sujatha Joshi': {'name': 'Dr. Sujatha Joshi',
   'email': 'sujatha.joshi@nnmit.ac.in'},
  'Dr. Roopa M S': {'name': 'Dr. Roopa M S', 'email': 'roopa.ms@nnmit.ac.in'},
  'Ms. Bhuvaneshwari P V': {'name': 'Ms. Bhuvaneshwari P V',
   'email': 'bhuvaneshwari.pv@nnmit.ac.in'}},
 'classes': [{'label': 'High Performance Computing',
   'day': 'Monday',
   'start': '09:00',
   'end': '09:55',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS71',
   'teacher_keys': ['Dr. Jayashree']},
  {'label': 'Cloud Computing',
   'day': 'Monday',
   'start': '11:00',
   'end': '11:55',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS74',
   'teacher_keys': ['Ms. Kavitha K K']},
  {'label': 'Deep Learning with Python',
   'day': 'Monday',
   'start': '12:35',
   'end': '13:30',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS771',
   'teacher_keys': ['Dr. Sujatha Joshi']},
  {'label': 'Internet Of Things',
   'day': 'Monday',
   'start': '12:35',
   'end': '13:30',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS772',
   'teacher_keys': ['Dr. Roopa M S']},
  {'label': 'Cyber Laws And Ethics',
   'day': 'Monday',
   'start': '12:35',
   'end': '13:30',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS773',
   'teacher_keys': ['Ms. Bhuvaneshwari P V']},
  {'label': 'Blockchain Technology',
   'day': 'Monday',
   'start': '12:35',
   'end': '13:30',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS774',
   'teacher_keys': ['Dr. P Ramesh Naidu']},
  {'label': 'Cloud Computing',
   'day': 'Monday',
   'start': '13:30',
   'end': '14:25',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS74',
   'teacher_keys': ['Ms. Kavitha K K']},
  {'label': 'Green Computing Lab',
   'day': 'Tuesday',
   'start': '09:00',
   'end': '09:55',
   'type': 'L',
   'room': None,
   'subject_code': '22CS73',
   'teacher_keys': ['Dr. P Ramesh Naidu', 'Ms. Kavitha K K']},
  {'label': 'Cloud Computing',
   'day': 'Tuesday',
   'start': '10:05',
   'end': '11:00',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS74',
   'teacher_keys': ['Ms. Kavitha K K']},
  {'label': 'High Performance Computing',
   'day': 'Tuesday',
   'start': '11:00',
   'end': '11:55',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS71',
   'teacher_keys': ['Dr. Jayashree']},
  {'label': 'Deep Learning with Python',
   'day': 'Tuesday',
   'start': '12:35',
   'end': '13:30',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS771',
   'teacher_keys': ['Dr. Sujatha Joshi']},
  {'label': 'Internet Of Things',
   'day': 'Tuesday',
   'start': '12:35',
   'end': '13:30',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS772',
   'teacher_keys': ['Dr. Roopa M S']},
  {'label': 'Cyber Laws And Ethics',
   'day': 'Tuesday',
   'start': '12:35',
   'end': '13:30',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS773',
   'teacher_keys': ['Ms. Bhuvaneshwari P V']},
  {'label': 'Blockchain Technology',
   'day': 'Tuesday',
   'start': '12:35',
   'end': '13:30',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS774',
   'teacher_keys': ['Dr. P Ramesh Naidu']},
  {'label': 'Cloud Computing',
   'day': 'Tuesday',
   'start': '13:30',
   'end': '14:25',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS74',
   'teacher_keys': ['Ms. Kavitha K K']},
  {'label': 'Green Computing',
   'day': 'Tuesday',
   'start': '15:20',
   'end': '16:15',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS73',
   'teacher_keys': ['Dr. Saroja Devi H']},
  {'label': 'Cyber Security',
   'day': 'Wednesday',
   'start': '09:00',
   'end': '09:55',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS72',
   'teacher_keys': ['Dr. Janardhana D R']},
  {'label': 'Full Stack Development',
   'day': 'Wednesday',
   'start': '10:05',
   'end': '11:00',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS75',
   'teacher_keys': ['Dr. P Ramesh Naidu']},
  {'label': 'Cyber Security',
   'day': 'Wednesday',
   'start': '11:00',
   'end': '11:55',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS72',
   'teacher_keys': ['Dr. Janardhana D R']},
  {'label': 'High Performance Computing',
   'day': 'Wednesday',
   'start': '12:35',
   'end': '13:30',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS71',
   'teacher_keys': ['Dr. Jayashree']},
  {'label': 'Full Stack Development',
   'day': 'Wednesday',
   'start': '13:30',
   'end': '14:25',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS75',
   'teacher_keys': ['Dr. P Ramesh Naidu']},
  {'label': 'Cloud Computing',
   'day': 'Wednesday',
   'start': '14:25',
   'end': '15:20',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS74',
   'teacher_keys': ['Ms. Kavitha K K']},
  {'label': 'Green Computing',
   'day': 'Wednesday',
   'start': '15:20',
   'end': '16:15',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS73',
   'teacher_keys': ['Dr. Saroja Devi H']},
  {'label': 'Full Stack Development',
   'day': 'Thursday',
   'start': '09:00',
   'end': '09:55',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS75',
   'teacher_keys': ['Dr. P Ramesh Naidu']},
  {'label': 'High Performance Computing',
   'day': 'Thursday',
   'start': '10:05',
   'end': '11:00',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS71',
   'teacher_keys': ['Dr. Jayashree']},
  {'label': 'Cloud Computing',
   'day': 'Thursday',
   'start': '11:00',
   'end': '11:55',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS74',
   'teacher_keys': ['Ms. Kavitha K K']},
  {'label': 'Full Stack Development',
   'day': 'Thursday',
   'start': '12:35',
   'end': '13:30',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS75',
   'teacher_keys': ['Dr. P Ramesh Naidu']},
  {'label': 'Cyber Security',
   'day': 'Thursday',
   'start': '13:30',
   'end': '14:25',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS72',
   'teacher_keys': ['Dr. Janardhana D R']},
  {'label': 'High Performance Computing Lab',
   'day': 'Thursday',
   'start': '14:25',
   'end': '15:20',
   'type': 'L',
   'room': 'RM',
   'subject_code': '22CS76',
   'teacher_keys': ['Dr. Jayashree', 'Dr. Janardhana D R', 'Dr. N Jayasree']},
  {'label': 'High Performance Computing Lab',
   'day': 'Thursday',
   'start': '15:20',
   'end': '16:15',
   'type': 'L',
   'room': 'RM',
   'subject_code': '22CS76',
   'teacher_keys': ['Dr. Jayashree', 'Dr. Janardhana D R', 'Dr. N Jayasree']},
  {'label': 'Cyber Security',
   'day': 'Friday',
   'start': '09:00',
   'end': '09:55',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS72',
   'teacher_keys': ['Dr. Janardhana D R']},
  {'label': 'Full Stack Development',
   'day': 'Friday',
   'start': '10:05',
   'end': '11:00',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS75',
   'teacher_keys': ['Dr. P Ramesh Naidu']},
  {'label': 'Green Computing',
   'day': 'Friday',
   'start': '11:00',
   'end': '11:55',
   'type': 'T',
   'room': '236B',
   'subject_code': '22CS73',
   'teacher_keys': ['Dr. Saroja Devi H']},
  {'label': 'Cloud Computing Lab',
   'day': 'Friday',
   'start': '12:35',
   'end': '16:15',
   'type': 'L',
   'room': None,
   'subject_code': '22CS74',
   'teacher_keys': ['Ms. Kavitha K K']},
  {'label': 'High Performance Computing Lab',
   'day': 'Friday',
   'start': '12:35',
   'end': '16:15',
   'type': 'L',
   'room': None,
   'subject_code': '22CS71',
   'teacher_keys': ['Dr. Jayashree']},
  {'label': 'Green Computing Lab',
   'day': 'Friday',
   'start': '12:35',
   'end': '16:15',
   'type': 'L',
   'room': None,
   'subject_code': '22CS73',
   'teacher_keys': ['Dr. Saroja Devi H']},
  {'label': 'Full Stack Development Lab',
   'day': 'Friday',
   'start': '12:35',
   'end': '16:15',
   'type': 'L',
   'room': None,
   'subject_code': '22CS75',
   'teacher_keys': ['Dr. P Ramesh Naidu']},
  {'label': 'Deep Learning with Python Lab',
   'day': 'Saturday',
   'start': '09:00',
   'end': '16:15',
   'type': 'L',
   'room': None,
   'subject_code': '22CS771',
   'teacher_keys': ['Dr. Sujatha Joshi']},
  {'label': 'Internet Of Things Lab',
   'day': 'Saturday',
   'start': '09:00',
   'end': '16:15',
   'type': 'L',
   'room': None,
   'subject_code': '22CS772',
   'teacher_keys': ['Dr. Roopa M S']},
  {'label': 'Cyber Laws And Ethics Lab',
   'day': 'Saturday',
   'start': '09:00',
   'end': '16:15',
   'type': 'L',
   'room': None,
   'subject_code': '22CS773',
   'teacher_keys': ['Ms. Bhuvaneshwari P V']},
  {'label': 'Blockchain Technology Lab',
   'day': 'Saturday',
   'start': '09:00',
   'end': '16:15',
   'type': 'L',
   'room': None,
   'subject_code': '22CS774',
   'teacher_keys': ['Dr. P Ramesh Naidu']}]}


PASS1_PROMPT = """You are extracting timetable data from an image.

Return a SINGLE string that is valid JSON.
The output must be directly parsable using json.loads().
Do NOT include explanations.
Do NOT include markdown.
Do NOT include formatting markers of any kind.

The image structure:
- The UPPER part of the image contains a timetable grid with SUBJECT CODES in each class slot.
- The LOWER part of the image contains a mapping table that maps:
  - subject_code to subject_name
  - subject_code to teacher name(s)

Important interpretation rules:
- Subject codes always appear in the timetable grid.
- Full subject names and teacher names appear in the lower mapping table.
- Some subjects list only TEACHER INITIALS instead of full names.
  - Look for matching initials beside teacher names in the SAME COLUMN.
  - If a teacher cannot be confidently identified, skip that teacher.
- Some lab classes are handled by MULTIPLE teachers.
  - In that case, list ALL teachers for that class slot.
- If a timetable slot contains multiple subject codes, create SEPARATE class entries.

OUTPUT STRUCTURE (FOLLOW EXACTLY):

{
  "class_details": {
    "class_name": string,
    "department": string,
    "academic_year": string,
    "semester": string,
    "default_room": string | null
  },

  "subjects": {
    "subject_code": "subject_name"
  },

  "teachers": {
    "teacher_key": {
      "name": string,
      "email": string | null
    }
  },

  "classes": [
    {
      "label": string,
      "day": string,
      "start": "HH:MM",
      "end": "HH:MM",
      "type": "T" | "L",
      "room": string | null,
      "subject_code": string,
      "teacher_keys": [string]
    }
  ]
}

STRICT RULES:
- subjects and teachers are canonical lookup tables.
- classes MUST reference subjects by subject_code.
- classes MUST reference teachers by teacher_keys only.
- Do NOT repeat subject names or teacher names inside classes.
- Do NOT invent IDs.
- Do NOT invent subject codes, names, teacher names, emails, rooms, or times.
- If a value is unclear, omit that specific class entry.
- One class entry represents exactly ONE timetable slot.
- The final output must be valid JSON and nothing else.
"""

class TimetablePipeline:

    def __init__(self, *, vision_llm, conn, entity_ingestor):
        self.vision_llm = vision_llm    # vision Gemini
        self.conn = conn
        self.entity_ingestor = entity_ingestor

    def pass1_extract(self, text: str) -> dict:
        response = self.llm.invoke(text)

        try:
            return json.loads(response.content)
        except Exception as e:
            raise ValueError("Invalid JSON from Pass-1") from e

    def image_to_data_uri(self, *, image_path: str, max_width:int=1024) -> str:
      img = Image.open(image_path)

      if img.width > max_width:
          ratio = max_width / img.width
          new_size = (max_width, int(img.height * ratio))
          img = img.resize(new_size, Image.LANCZOS)

      buffer = io.BytesIO()
      img.save(buffer, format="PNG", optimize=True)
      encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")

      return f"data:image/png;base64,{encoded}"
    
    def _resolve_subject(self, *, subject_code: str, subject_name: str) -> UUID:
      with self.conn.cursor() as cur:
          cur.execute(
              "SELECT id FROM subjects WHERE subject_code = %s",
              (subject_code,)
          )
          row = cur.fetchone()
          if row:
              return row[0]

          cur.execute(
              """
              INSERT INTO subjects (subject_code, subject_name)
              VALUES (%s, %s)
              RETURNING id
              """,
              (subject_code, subject_name)
          )
          subject_id =  cur.fetchone()[0]

      self.entity_ingestor.ingest([{
          "entity_type": "subject",
          "entity_id": subject_id,
          "surface_form": subject_name,
          "source_table": "subjects",
          "embedding_text": [
            subject_name,
            subject_name.lower(),
            subject_name.title(),
            subject_code,
        ]
      }])

      return subject_id


    def _teacher_name_variants(self, name: str) -> list[str]:
        base = name.strip()

        variants = set()
        variants.add(base)
        variants.add(base.lower())
        variants.add(base.title())

        # remove dots
        no_dots = re.sub(r"\.", "", base)
        variants.add(no_dots)
        variants.add(no_dots.lower())
        variants.add(no_dots.title())

        # strip titles
        titles = r"^(dr|prof|mr|ms|mrs)\s+"
        stripped = re.sub(titles, "", base, flags=re.IGNORECASE)
        if stripped != base:
            variants.add(stripped)
            variants.add(stripped.lower())
            variants.add(stripped.title())

        # split parts
        parts = stripped.split()
        for p in parts:
            variants.add(p)
            variants.add(p.lower())
            variants.add(p.title())

        return list(variants)


      
    def _resolve_teacher(self, *, name: str, email: str | None) -> UUID:
      with self.conn.cursor() as cur:
          if email:
              cur.execute(
                  "SELECT id FROM teachers WHERE email = %s",
                  (email,)
              )
          else:
              cur.execute(
                  "SELECT id FROM teachers WHERE name = %s AND email IS NULL",
                  (name,)
              )

          row = cur.fetchone()
          if row:
              teacher_id = row[0]
          else:
              cur.execute(
                  """
                  INSERT INTO teachers (name, email)
                  VALUES (%s, %s)
                  RETURNING id
                  """,
                  (name, email)
              )
              teacher_id = cur.fetchone()[0]

      # ---- ENTITY INGESTION ----
      variants = self._teacher_name_variants(name)

      self.entity_ingestor.ingest([{
          "entity_type": "teacher",
          "entity_id": teacher_id,
          "surface_form": name,
          "source_table": "teachers",
          "embedding_text": variants
      }])

      return teacher_id

        
    def _insert_classes(
      self,
      *,
      classes: list[dict],
      subject_ids: dict,
      teacher_ids: dict,
      vision_output:dict
  ):
      with self.conn.cursor() as cur:
        for cls in classes:
            cur.execute(
            """
            INSERT INTO classes (
                class_name,
                day_of_week,
                start_time,
                end_time,
                type,
                room,
                label,
                class_teacher
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
              (
                vision_output["class_details"]["class_name"],
                cls["day"],
                cls["start"],
                cls["end"],
                cls["type"],
                cls["room"] or vision_output["class_details"]["default_room"],
                cls["label"],
                teacher_ids[cls["teacher_keys"][0]] if cls["teacher_keys"] else None
              )
            )

            class_id = cur.fetchone()[0]

            # subject join
            cur.execute(
                """
                INSERT INTO class_subjects (class_id, subject_id)
                VALUES (%s, %s)
                """,
                (class_id, subject_ids[cls["subject_code"]])
            )

            # teacher joins
            for teacher_key in cls["teacher_keys"]:
                cur.execute(
                    """
                    INSERT INTO class_teachers (class_id, teacher_id)
                    VALUES (%s, %s)
                    """,
                    (class_id, teacher_ids[teacher_key])
                )


    
    def _resolve(self, *, vision_output: dict):
      try:
          # 1. Resolve subjects
          subject_ids = {}
          for code, name in vision_output["subjects"].items():
              subject_ids[code] = self._resolve_subject(
                  subject_code=code,
                  subject_name=name
              )

          # 2. Resolve teachers
          teacher_ids = {}
          for key, value in vision_output["teachers"].items():
              teacher_ids[key] = self._resolve_teacher(
                  name=value["name"],
                  email=value.get("email")
              )

          # 3. Insert classes + joins
          self._insert_classes(
              classes=vision_output["classes"],
              subject_ids=subject_ids,
              teacher_ids=teacher_ids,
              vision_output=vision_output
          )

          self.conn.commit()

      except Exception:
          self.conn.rollback()
          raise
      
    def _extract_json(self, text: str) -> dict:
        if not isinstance(text, str):
            raise ValueError("LLM output is not text")

        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1 or end <= start:
            raise ValueError("No valid JSON object found in LLM output")

        json_str = text[start : end + 1]

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON after cleanup: {e}")




    def run(self, image_path: str, test:bool = False):
        if not test:
          image_data_uri = self.image_to_data_uri(image_path=image_path)

          vision_msg = HumanMessage(
              content=[
                  {"type": "text", "text": PASS1_PROMPT},
                  {"type": "image_url", "image_url": image_data_uri},
              ]
          )

          response = self.vision_llm.invoke([vision_msg])
          print(response)

          vision_output = self._extract_json(response.content)
        else:
          vision_output = test_output

        self._resolve(vision_output=vision_output)

