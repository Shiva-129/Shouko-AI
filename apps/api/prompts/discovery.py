import json
from pydantic import BaseModel, Field


class DiscoveryOutput(BaseModel):
    paper_id: str
    score: int = Field(ge=0, le=100)
    reason: str


SYSTEM_PROMPT = (
    "You are a research relevancy scoring AI. Given a user's research interest profile "
    "and a list of academic papers, score each paper's relevance to the user's interests "
    "on a scale of 0-100."
)


def build_user_prompt(profile: dict, papers_data: list[dict]) -> str:
    topics = profile.get("topics", [])
    keywords = profile.get("keywords", [])
    authors = profile.get("authors", [])
    categories = profile.get("categories", [])

    profile_str = (
        f"User Interest Profile:\n"
        f"- Topics: {topics or ['General ML/AI']}\n"
        f"- Keywords: {keywords or []}\n"
        f"- Authors of interest: {authors or []}\n"
        f"- Categories: {categories or []}"
    )

    papers_str = json.dumps(papers_data, indent=2)

    return (
        f"{profile_str}\n\n"
        f"Papers to score:\n{papers_str}\n\n"
        "Return a JSON array of objects with keys: paper_id, score (integer 0-100), "
        "reason (short 1-sentence explanation).\n"
        "Only return valid JSON, nothing else."
    )
