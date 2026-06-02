PROMPT_VERSION = "1.0"

SYSTEM_PROMPT = (
    "You are PaperBrain-AI, a world-class academic research intelligence assistant.\n"
    "Your objective is to provide highly precise, technical, and scientifically accurate answers "
    "based strictly on the extracted context chunks of the academic paper provided.\n\n"
    "Rules:\n"
    "1. Ground your answers thoroughly in the provided text snippets.\n"
    "2. If the context does not contain enough information to answer a question, state this clearly while providing "
    "related context about the scientific domain if available.\n"
    "3. Use LaTeX formatting for mathematical expressions where appropriate (e.g. $E = mc^2$ or $$E=mc^2$$)."
)


def build_user_prompt(query: str, context_chunks: list[dict], history: list[dict]) -> str:
    # Build context string
    context_str = ""
    for i, c in enumerate(context_chunks):
        context_str += f"--- CONTEXT CHUNK #{i+1} (Page {c.get('page_number', 1)}, Section: {c.get('section', 'body')}) ---\n"
        context_str += f"{c['content']}\n\n"

    # Build history log
    history_str = ""
    for msg in history[-6:]:  # Keep last 6 interactions
        role_label = "User" if msg["role"] == "user" else "Assistant"
        history_str += f"{role_label}: {msg['content']}\n"

    return (
        f"Here is the context extracted from the academic paper:\n\n"
        f"{context_str}"
        f"Here is our recent conversation history:\n"
        f"{history_str}\n"
        f"Current Question: {query}\n\n"
        f"Provide a structured, deep academic answer:"
    )
