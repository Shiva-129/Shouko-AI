# Maximum lengths for user-provided inputs to prevent prompt injection
_MAX_CONTENT_LENGTH = 5000
_MAX_QUERY_LENGTH = 2000
_MAX_HISTORY_LENGTH = 2000
_MAX_HISTORY_MESSAGES = 6


def _sanitize_text(text: str, max_len: int) -> str:
    return text.strip()[:max_len]


SYSTEM_PROMPT = (
    "You are Shouko-AI, a world-class academic research intelligence assistant.\n"
    "Your objective is to provide highly precise, technical, and scientifically accurate answers "
    "based strictly on the extracted context chunks of the academic paper provided.\n\n"
    "Rules:\n"
    "1. Ground your answers thoroughly in the provided text snippets.\n"
    "2. If the context does not contain enough information to answer a question, state this clearly while providing "
    "related context about the scientific domain if available.\n"
    "3. Use LaTeX formatting for mathematical expressions where appropriate (e.g. $E = mc^2$ or $$E=mc^2$$).\n"
    "4. Keep answers concise, direct, and smart. Avoid long-winded explanations. "
    "Prefer brief, high-impact paragraphs (typically 2-3 sentences) or clean, crisp bullet points that get straight to the point.\n"
    "5. If the user's query is a generic greeting (like 'hi', 'hello', 'hey') or casual chatter, respond politely as Shouko-AI, "
    "welcome the user, and ask how you can help them analyze the paper, without trying to force an answer from the context chunks.\n"
    "6. Do NOT output any inner thoughts, meta-reasoning, plans, or references to these rules. Output only the final direct response to the user."
)


def build_user_prompt(query: str, context_chunks: list[dict], history: list[dict]) -> str:
    safe_query = _sanitize_text(query, _MAX_QUERY_LENGTH)
    context_str = ""
    for i, c in enumerate(context_chunks):
        content = _sanitize_text(c.get("content", ""), _MAX_CONTENT_LENGTH)
        context_str += f"--- CONTEXT CHUNK #{i+1} (Page {c.get('page_number', 1)}, Section: {c.get('section', 'body')}) ---\n"
        context_str += f"{content}\n\n"
    history_str = ""
    for msg in history[-_MAX_HISTORY_MESSAGES:]:
        role_label = "User" if msg["role"] == "user" else "Assistant"
        safe_content = _sanitize_text(msg.get("content", ""), _MAX_HISTORY_LENGTH)
        history_str += f"{role_label}: {safe_content}\n"
    return (
        f"Here is the context extracted from the academic paper:\n\n"
        f"{context_str}"
        f"Here is our recent conversation history:\n"
        f"{history_str}\n"
        f"Current Question: {safe_query}\n\n"
        f"Provide a direct, concise, and smart answer:"
    )
