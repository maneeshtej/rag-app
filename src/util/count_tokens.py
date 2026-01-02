def count_tokens(prompt: str) -> int:
    # Gemini ~ 4 chars per token (rough)
    return len(prompt) // 4
