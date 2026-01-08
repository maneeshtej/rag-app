from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder



class AnswerPipeline:
    def __init__(self, llm, history_size=3, prompt=None):
        self.llm = llm
        self.history_size= history_size
        self.prompt = prompt or self._default_prompt()

    def _build_context(
        self,
        *,
        vector_docs: list[Document],
        sql_rows: list[dict],
    ) -> str:
        parts = []

        if sql_rows:
            parts.append("DATABASE RESULTS:")
            for row in sql_rows:
                parts.append(
                    "- " + ", ".join(f"{k}: {v}" for k, v in row.items())
                )

        if vector_docs:
            parts.append("\nREFERENCE DOCUMENTS:")
            for i, doc in enumerate(vector_docs, 1):
                parts.append(f"[Doc {i}] {doc.page_content}")

        return "\n".join(parts).strip()


    def _default_prompt(self):
        return ChatPromptTemplate.from_messages([
            (
                "system",
                """
    You are a STRICT answer-generation assistant.

    You are given:
    - DATABASE RESULTS (structured, authoritative)
    - REFERENCE DOCUMENTS (unstructured text)

    Your job is to decide WHICH source can correctly answer the question,
    and produce the final answer.

    SELECTION RULES (MANDATORY):

    1. If DATABASE RESULTS are present AND they directly answer the question:
    - Use ONLY DATABASE RESULTS
    - Ignore reference documents completely

    2. If DATABASE RESULTS are present BUT do NOT answer the question:
    - Ignore them
    - Use REFERENCE DOCUMENTS if relevant

    3. If DATABASE RESULTS are empty AND reference documents contain relevant information:
    - Answer using reference documents

    4. If NEITHER source can answer the question:
    - Respond EXACTLY with: "I don't know."

    CONTENT RULES (STRICT):

    - Use ONLY the provided context
    - Do NOT use prior knowledge
    - Do NOT infer missing facts
    - Do NOT explain your reasoning
    - Do NOT mention databases, SQL, vectors, or documents
    - Produce clear, direct, human-readable answers

    FORMAT RULES:

    - If listing items, use bullet points
    - If a single fact, use a single sentence
    - No preambles, no disclaimers
    """
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




    
    def run(
        self,
        query: str,
        vector_docs: list[Document] = [],
        sql_rows: list[dict] = [],
        chat_history=None,
    ):
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



    
        
