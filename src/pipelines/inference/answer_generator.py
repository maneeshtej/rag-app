from typing import List
from src.models.retrieved_chunk import RetrievedChunk


class AnswerGenerator:
    def __init__(self, *, llm):
        """
        llm must expose: generate(prompt: str) -> str
        """
        self.llm = llm

    def _build_prompt(
        self,
        *,
        query: str,
        chunks: List[RetrievedChunk],
    ) -> str:
        context_blocks = []

        for i, c in enumerate(chunks, start=1):
            context_blocks.append(
                f"[{i}] Source: {c.source}\n{c.content}"
            )

        context = "\n\n".join(context_blocks)

        return f"""
You are a factual assistant.
Answer ONLY using the provided context.
If the answer is not present, say "I don't know".

Context:
{context}

Question:
{query}

Answer:
""".strip()

    def generate(
        self,
        *,
        query: str,
        chunks: List[RetrievedChunk],
    ) -> dict:
        # guardrail
        if not chunks:
            return {
                "answer": "I don't know",
                "citations": [],
            }

        prompt = self._build_prompt(
            query=query,
            chunks=chunks,
        )

        answer = self.llm.invoke(prompt)

        return {
            "answer": answer.content.strip(),
            "citations": [
                {
                    "chunk_id": str(c.chunk_id),
                    "source": c.source,
                }
                for c in chunks
            ],
        }
