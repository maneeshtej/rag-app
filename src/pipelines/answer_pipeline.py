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
                (
                    "You are a strict retrieval-based assistant.\n\n"
                    "Rules you MUST follow:\n"
                    "1. Use ONLY the information provided in the Context.\n"
                    "2. If the Context is empty, respond exactly with: \"I don't know.\".\n"
                    "3. If the answer to the Question is NOT explicitly stated in the Context, "
                    "respond exactly with: \"I don't know.\".\n"
                    "4. Do NOT use prior knowledge, assumptions, or reasoning beyond the Context.\n"
                    "5. Do NOT explain why you don't know.\n"
                    "6. Do NOT add any information that is not present in the Context.\n"
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



    
    def run(self, query:str, vector_docs:list[Document]=[], sql_rows:list[dict]=[], chat_history=None):

        chat_history = chat_history or []

        docs = self._build_context(vector_docs=vector_docs, sql_rows=sql_rows)

        context = docs
        messages = self.prompt.format_messages(
            context=context,
            question=query,
            chat_history=chat_history
        )

        print(f"token count inference: {len(messages) // 4}")
        # print(messages)

        response = self.llm.invoke(messages)

        return response.content

    
        
