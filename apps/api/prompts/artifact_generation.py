from pydantic import BaseModel, Field


class Insight(BaseModel):
    insight: str = Field(..., description="One clear, specific insight from the paper")
    importance_score: int = Field(..., ge=1, le=10, description="Importance of this insight (1-10)")
    section: str | None = Field(None, description="Which section this insight comes from")


class QAPair(BaseModel):
    question: str = Field(..., description="A meaningful question a researcher would ask")
    answer: str = Field(..., description="Detailed answer grounded in the paper's content")
    difficulty: str = Field("medium", description="EASY, MEDIUM, or HARD")


class SuggestedExperiment(BaseModel):
    title: str = Field(..., description="Short experiment title")
    description: str = Field(..., description="Concrete steps to run the experiment")
    feasibility: str = Field("medium", description="EASY, MEDIUM, or HARD")


class ArtifactOutput(BaseModel):
    one_line_summary: str = Field(..., description="Tweet-length summary (max 280 chars)")
    summary: str = Field(..., description="Plain English summary, max 300 words")
    key_insights: list[Insight] = Field(..., description="5-8 key insights with importance scores")
    auto_qa: list[QAPair] = Field(..., description="10-15 Q&A pairs covering the paper")
    suggested_experiments: list[SuggestedExperiment] = Field(
        ..., description="3-5 concrete experiments to build on this work"
    )


SYSTEM_PROMPT = (
    "You are an expert AI research analyst. Given a paper's full text chunks, "
    "generate a structured knowledge artifact that helps a researcher quickly "
    "understand the paper's contributions, key insights, and how to build on it.\n\n"
    "Rules:\n"
    "- Only use information explicitly stated in the provided chunks — do not hallucinate.\n"
    "- If the chunks lack information for a section, mark it with 'Insufficient information in source.'\n"
    "- Write in clear, plain English suitable for a PhD-level researcher.\n"
    "- Insights must be specific and technical, not generic praise.\n"
    "- Q&A pairs should cover: core contribution, methodology, key results, limitations, and future work.\n"
    "- Experiments must be concrete and reproducible.\n"
    "- Return ONLY valid JSON matching the required schema — no markdown, no preamble, no explanation."
)


def build_artifact_prompt(paper_title: str, paper_abstract: str | None, chunks: list[dict]) -> str:
    sections: dict[str, list[str]] = {}
    for c in chunks:
        section = c.get("section", "body") or "body"
        if section not in sections:
            sections[section] = []
        sections[section].append(c["content"])

    context_parts = [f"# Paper: {paper_title}"]
    if paper_abstract:
        context_parts.append(f"\n## Abstract\n{paper_abstract}")

    for section_name in ["abstract", "introduction", "methods", "body", "references"]:
        if section_name in sections:
            block = "\n\n".join(sections[section_name][:3])
            context_parts.append(f"\n## {section_name.capitalize()}\n{block}")

    context = "\n\n---\n\n".join(context_parts)

    return (
        f"{context}\n\n"
        "Generate a structured artifact with:\n"
        "- one_line_summary: string (max 280 chars)\n"
        "- summary: string (max 300 words)\n"
        "- key_insights: array of {insight: string, importance_score: int (1-10), section: string | null} (5-8 items)\n"
        "- auto_qa: array of {question: string, answer: string, difficulty: 'EASY' | 'MEDIUM' | 'HARD'} (10-15 items)\n"
        "- suggested_experiments: array of {title: string, description: string, feasibility: 'EASY' | 'MEDIUM' | 'HARD'} (3-5 items)\n\n"
        "Return ONLY valid JSON, nothing else."
    )
