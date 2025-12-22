from typing import List
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser


class AnswerPipeline:
    def __init__(self, llm, reranker=None, history_size=3, prompt=None):
        self.llm = llm
        self.reranker = reranker
        self.history_size= history_size
        self.prompt = prompt or self.default_prompt()

    def set_reranker(self, reranker):
        self.reranker = reranker

    def default_prompt(self):
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

    
    def run(self, query:str, docs:List[Document], chat_history=None):

        chat_history = chat_history or []

        if self.reranker:
            docs = self.reranker.rerank(query, docs)

        context = "\n\n".join(doc.page_content for doc in docs)

        messages = self.prompt.format_messages(
            context=context,
            question=query,
            chat_history=chat_history
        )

        response = self.llm.invoke(messages)

        return response.content

    
        
