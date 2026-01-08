import json
import uuid

from src.models.user import User
from langchain_core.documents import Document


class ScrapeIngestionPipeline:
    def __init__(self, sql_ingester, sql_retriever, vector_ingestor, embedder):
        self.sql_ingester = sql_ingester
        self.sql_retriever = sql_retriever
        self.vector_ingestor = vector_ingestor
        self.embedder = embedder

    # ---------- helpers ----------

    def _get_department(self, dept_name: str) -> dict:
        rows = self.sql_retriever.sql_store.resolve_entity(
            table="departments",
            columns=["name", "short_code", "aliases"],
            value=dept_name,
            k=1,
        )
        if not rows:
            raise ValueError(f"Department not found: {dept_name}")
        return rows[0]

    def _parse_experience(self, exp: str | None):
        if not exp:
            return None
        digits = "".join(c for c in exp if c.isdigit())
        return int(digits) if digits else None

    def _build_faculty_objects(self, raw_profiles: list[dict]) -> list[dict]:
        faculty_objs = []

        for p in raw_profiles:
            faculty_objs.append({
                "name": p["name"],
                "designation": p["designation"],
                "email": p.get("email"),
                "contact_no": p.get("contact_no."),
                "joining_date": p.get("joining_date"),
                "experience_years": self._parse_experience(
                    p.get("past_experience")
                ),
                "subjects": self._normalize_list(p.get("subjects_taught")),
            })

        return faculty_objs
    
    def _normalize_list(self, val):
        if not val:
            return []
        if isinstance(val, list):
            return [v.strip() for v in val if v.strip()]
        if isinstance(val, str):
            return [v.strip() for v in val.split(",") if v.strip()]
        return []


    # ---------- ingestion ----------

    def _ingest_faculty(self, *, faculty_objs: list[dict], dept_id: str) -> dict:
        faculty_map = {}

        for obj in faculty_objs:
            faculty_id = str(uuid.uuid4())

            self.sql_ingester.ingest(
                sql_obj={
                    "table": "faculty",
                    "action": "insert",
                    "data": {
                        "id": faculty_id,
                        "name": obj["name"],
                        "designation": obj["designation"],
                        "email": obj["email"],
                        "contact_no": obj["contact_no"],
                        "joining_date": obj["joining_date"],
                        "experience_years": obj["experience_years"],
                        "department_id": dept_id,
                    },
                }
            )

            faculty_map[obj["name"]] = {
                "id": faculty_id,
                "subjects": obj["subjects"],  # kept for later mapping
            }

        return faculty_map
    
    def _ensure_subjects(
        self,
        *,
        faculty_map: dict,
        dept_id: str,
    ) -> dict:
        """
        Returns:
        {
        subject_name: {
            "subject_id": <uuid>,
            "faculty_ids": [<faculty_id>, ...]
        }
        }
        """
        subject_map = {}

        for faculty_name, fdata in faculty_map.items():
            faculty_id = fdata["id"]

            for subj in fdata["subjects"]:
                entry = subject_map.get(subj)

                if not entry:
                    rows = self.sql_retriever.sql_store.resolve_entity(
                        table="subjects",
                        columns=["name"],
                        value=subj,
                        k=1,
                    )

                    if rows:
                        subject_id = rows[0]["id"]
                    else:
                        subject_id = str(uuid.uuid4())
                        self.sql_ingester.ingest(
                            sql_obj={
                                "table": "subjects",
                                "action": "insert",
                                "data": {
                                    "id": subject_id,
                                    "name": subj,
                                    "code": subj[:10].upper().replace(" ", "_"),
                                    "department_id": dept_id,
                                },
                            }
                        )


                    subject_map[subj] = {
                        "subject_id": subject_id,
                        "faculty_ids": set(),
                    }


                subject_map[subj]["faculty_ids"].add(faculty_id)

        return subject_map


    def _map_faculty_subjects(
        self,
        *,
        subject_map: dict,
        dept_id: str,
    ):
        """
        Inserts rows into faculty_subjects using subject_map.
        """
        for data in subject_map.values():
            subject_id = data["subject_id"]

            for faculty_id in data["faculty_ids"]:
                self.sql_ingester.ingest(
                    sql_obj={
                        "table": "faculty_subjects",
                        "action": "insert",
                        "data": {
                            "id": str(uuid.uuid4()),
                            "faculty_id": faculty_id,
                            "subject_id": subject_id,
                            "department_id": dept_id
                        },
                    }
                )

    def _faculty_surface_forms(self, name: str) -> set[str]:
        forms = set()

        base = name.strip()
        lower = base.lower()

        forms.add(base)
        forms.add(lower)

        for title in ["Prof", "Professor", "Dr"]:
            forms.add(f"{title} {base}")
            forms.add(f"{title.lower()} {lower}")

        tokens = lower.split()
        if len(tokens) == 2:
            forms.add(f"{tokens[1]} {tokens[0]}")  # reorder

        return forms
    
    def _ingest_faculty_entity_embeddings(
        self,
        *,
        faculty_map: dict,
    ):
        for name, data in faculty_map.items():
            faculty_id = data["id"]

            for surface in self._faculty_surface_forms(name):
                vec = self.embedder.embed_query(surface)

                self.sql_ingester.ingest(
                    sql_obj={
                        "table": "entity_embeddings",
                        "action": "insert",
                        "data": {
                            "entity_type": "faculty",
                            "entity_id": faculty_id,
                            "surface_form": surface,
                            "embedding": vec,
                        },
                    }
                )


    def _ingest_subject_entity_embeddings(
        self,
        *,
        subject_map: dict,
    ):
        for subject_name, data in subject_map.items():
            subject_id = data["subject_id"]

            forms = {
                subject_name,
                subject_name.lower(),
                subject_name.replace(" ", ""),
            }

            for surface in forms:
                vec = self.embedder.embed_query(surface)

                self.sql_ingester.ingest(
                    sql_obj={
                        "table": "entity_embeddings",
                        "action": "insert",
                        "data": {
                            "entity_type": "subject",
                            "entity_id": subject_id,
                            "surface_form": surface,
                            "embedding": vec,
                        },
                    }
                )







    def _ingest_vector(
        self,
        *,
        raw_profiles: list[dict],
        faculty_map: dict,
        dept_id: str,
        user:User
    ):
        """
        Build and ingest vector chunks per faculty.
        Chunking policy:
        - one faculty = multiple semantic chunks
        """

        docs = []

        for profile in raw_profiles:
            name = profile["name"]
            faculty_id = faculty_map[name]["id"]

            base_meta = {
                "entity": "faculty",
                "faculty_id": faculty_id,
                "department_id": dept_id,
                "owner_id": user.id,
                "access_level":user.access_level,
                "role":user.role,
                "source": "faculty"
            }

            # --- core profile chunk ---
            core_fields = {
                "name": profile.get("name"),
                "designation": profile.get("designation"),
                "email": profile.get("email"),
                "joining_date": profile.get("joining_date"),
                "experience": profile.get("past_experience"),
            }

            docs.append(
                Document(
                    page_content=json.dumps(core_fields, ensure_ascii=False),
                    metadata={**base_meta, "chunk_type": "faculty_core"},
                )
            )

            # --- subjects chunk ---
            if profile.get("subjects_taught"):
                docs.append(
                    Document(
                        page_content=json.dumps(
                            profile["subjects_taught"], ensure_ascii=False
                        ),
                        metadata={**base_meta, "chunk_type": "subjects"},
                    )
                )

            # --- research / interests ---
            for field in [
                "areas_of_interest",
                "sponsored_research_project",
                "research_profile",
                "achievement",
                "others",
            ]:
                if profile.get(field):
                    docs.append(
                        Document(
                            page_content=json.dumps(
                                profile[field], ensure_ascii=False
                            ),
                            metadata={**base_meta, "chunk_type": field},
                        )
                    )

        # delegate actual storage
        return self.vector_ingestor.ingest_documents(docs)




    # ---------- public API ----------

    def truncate_tables(self, *, tables: list[str]):
        return self.sql_ingester.truncate_tables(tables=tables)

    def ingest_faculty_profiles(
        self,
        *,
        profiles: list[dict],
        dept_name: str,
        user: User,
    ):
        dept = self._get_department(dept_name)
        dept_id = dept["id"]

        faculty_objs = self._build_faculty_objects(profiles)
        faculty_map = self._ingest_faculty(
            faculty_objs=faculty_objs,
            dept_id=dept_id,
        )

        subject_map = self._ensure_subjects(
            faculty_map=faculty_map,
            dept_id=dept_id
        )
        self._map_faculty_subjects(
            subject_map=subject_map,
            dept_id=dept_id
        )

        self._ingest_faculty_entity_embeddings(faculty_map=faculty_map)
        self._ingest_subject_entity_embeddings(subject_map=subject_map)

        vector = self._ingest_vector(
            raw_profiles=profiles,
            faculty_map=faculty_map,
            dept_id=dept_id,
            user=user
        )

        return {
            "department_id": dept_id,
            "faculty": faculty_map,
            "subjects": subject_map,
            "vector": vector
        }
