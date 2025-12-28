from typing import Dict, List
from uuid import uuid4
from langchain_core.documents import Document
from src.models.user import User


def schema_to_documents(
    schema: Dict[str, str],
    user: User,
) -> List[Document]:
    """
    Converts SQL schema definitions into LangChain Documents.
    One table = one document (one vector chunk later).
    """

    documents: List[Document] = []

    for table_name, table_text in schema.items():
        documents.append(
            Document(
                page_content=table_text.strip(),
                metadata={
                    "id": str(uuid4()),
                    "owner_id": str(user.id),
                    "role": user.role,
                    # schema should be globally readable
                    "access_level": user.access_level,
                    # one logical schema file
                    "source": "schema:all",
                    # schema-specific metadata
                    "table_is_true": True,
                    "table_name": table_name,
                    "doc_type": "sql_schema",
                },
            )
        )

    return documents
