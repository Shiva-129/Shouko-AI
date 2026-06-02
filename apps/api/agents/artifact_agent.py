import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.paper import Paper
from models.chunk import PaperChunk
from models.artifact import Artifact
from services.llm_service import LLMService
from prompts.artifact_generation import (
    SYSTEM_PROMPT, build_artifact_prompt, ArtifactOutput,
)


class ArtifactAgent:
    MAX_CHUNKS_PER_SECTION = 3

    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm = LLMService()

    async def generate(self, paper_id: str, artifact_id: str) -> ArtifactOutput | None:
        paper = await self._load_paper(paper_id)
        if not paper:
            raise ValueError(f"Paper {paper_id} not found")

        chunks = await self._load_chunks(paper_id)
        if not chunks:
            raise ValueError(f"No chunks found for paper {paper_id}")

        prompt = build_artifact_prompt(paper.title, paper.abstract, chunks)

        for attempt in range(3):
            try:
                raw = await self.llm.generate_completion(
                    system_prompt=SYSTEM_PROMPT,
                    prompt=prompt,
                    temperature=0.3,
                    max_tokens=8192,
                    model_override="gemini-1.5-flash",
                )
                raw = raw.strip()
                raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                parsed = json.loads(raw)
                validated = ArtifactOutput(**parsed)
                await self._store_artifact(artifact_id, validated)
                return validated
            except Exception as e:
                print(f"[ArtifactAgent] Attempt {attempt + 1}/3 failed: {e}")
                if attempt == 2:
                    await self._mark_failed(artifact_id, str(e))

        return None

    async def _load_paper(self, paper_id: str) -> Paper | None:
        result = await self.db.execute(select(Paper).where(Paper.id == paper_id))
        return result.scalar_one_or_none()

    async def _load_chunks(self, paper_id: str) -> list[dict]:
        result = await self.db.execute(
            select(PaperChunk)
            .where(PaperChunk.paper_id == paper_id)
            .order_by(PaperChunk.chunk_index)
        )
        chunks = result.scalars().all()

        sections: dict[str, list[dict]] = {}
        for c in chunks:
            section = c.section or "body"
            if section not in sections:
                sections[section] = []
            if len(sections[section]) < self.MAX_CHUNKS_PER_SECTION:
                sections[section].append({
                    "content": c.content,
                    "chunk_index": c.chunk_index,
                    "section": c.section,
                    "page_number": c.page_number,
                })

        ordered = []
        for section_name in ["abstract", "introduction", "methods", "body", "conclusion", "references"]:
            ordered.extend(sections.get(section_name, []))

        for section_name, section_chunks in sections.items():
            if section_name not in ["abstract", "introduction", "methods", "body", "conclusion", "references"]:
                ordered.extend(section_chunks)

        return ordered

    async def _store_artifact(self, artifact_id: str, output: ArtifactOutput):
        result = await self.db.execute(select(Artifact).where(Artifact.id == artifact_id))
        artifact = result.scalar_one_or_none()
        if not artifact:
            return

        artifact.one_line_summary = output.one_line_summary
        artifact.summary = output.summary
        artifact.key_insights = [i.model_dump() for i in output.key_insights]
        artifact.auto_qa = [q.model_dump() for q in output.auto_qa]
        artifact.suggested_experiments = [e.model_dump() for e in output.suggested_experiments]
        artifact.status = "ready"
        await self.db.flush()

    async def _mark_failed(self, artifact_id: str, error: str):
        result = await self.db.execute(select(Artifact).where(Artifact.id == artifact_id))
        artifact = result.scalar_one_or_none()
        if not artifact:
            return
        artifact.status = "failed"
        artifact.error_message = error
        await self.db.flush()
