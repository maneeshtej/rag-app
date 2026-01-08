from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder



class AnswerPipeline:
    def __init__(self, llm, history_size=3, prompt=None):
        self.llm = llm
        self.history_size= history_size
        self.prompt = prompt or self._default_prompt()

    def _default_prompt(self):
        return ChatPromptTemplate.from_messages([
            (
                "system",
                ("""
                    You are a strict retrieval-based assistant.

            Rules you MUST follow:

            1. Use ONLY the information provided in the Context.
            2. You MAY summarize, rephrase, or format the information into clear natural language.
            3. Do NOT use prior knowledge or assumptions beyond the Context.

            DATABASE RESULTS RULES:
            4. If DATABASE RESULTS are present and contain rows:
            - Treat them as authoritative.
            - Answer the question using those rows.
            - Present the answer in clear, human-readable English.
            5. If DATABASE RESULTS are empty but reference documents are present:
            - Answer using the reference documents.
            6. If BOTH DATABASE RESULTS and reference documents are empty:
            - Respond exactly with: "I don't know."

            OUTPUT RULES:
            7. Do NOT explain your reasoning.
            8. Do NOT mention SQL, databases, or documents.
            9. Do NOT add information not present in the Context.
            """
                )
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            (
                "human",
                (
                    "Context:\n"
                    "{context}\n\n"
                    "Question:\n"
                    "{question}"
                )
            ),
        ])
    
    def _build_context(
        self,
        *,
        vector_docs: list[Document],
        sql_rows: list[dict],
    ) -> str:
        parts: list[str] = []

        if sql_rows:
            if sql_rows:
                parts.append("DATABASE RESULTS:")

            for row in sql_rows:
                line = ", ".join(f"{k}: {v}" for k, v in row.items())
                parts.append(f"- {line}")

        if vector_docs:
            parts.append("\nREFERENCE DOCUMENTS:")
            for i, doc in enumerate(vector_docs, 1):
                parts.append(f"[Doc {i}]")
                parts.append(doc.page_content)

        return "\n".join(parts).strip()



    
    def run(
        self,
        query: str,
        vector_docs: list[Document] = [],
        sql_rows: list[dict] = [],
        chat_history=None,
    ):
        # 🔒 SQL-FIRST RULE
        if sql_rows:
            # Flatten rows safely
            if isinstance(sql_rows, list) and isinstance(sql_rows[0], dict):
                return "\n".join(
                    "- " + ", ".join(str(v) for v in row.values())
                    for row in sql_rows
                )

        # fallback to RAG
        chat_history = chat_history or []
        context = self._build_context(
            vector_docs=vector_docs,
            sql_rows=sql_rows,
        )

        messages = self.prompt.format_messages(
            context=context,
            question=query,
            chat_history=chat_history,
        )

        response = self.llm.invoke(messages)
        return response.content


    
        
