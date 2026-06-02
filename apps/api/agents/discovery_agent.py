import json
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from services.llm_service import LLMService
from prompts.discovery import SYSTEM_PROMPT, build_user_prompt
from core.config import settings


class DiscoveryAgent:
    BATCH_SIZE = 20

    def __init__(self, db: AsyncSession | None = None):
        self.db = db
        self.llm = LLMService()
        self._groq_client: AsyncOpenAI | None = None
        if settings.GROQ_API_KEY:
            self._groq_client = AsyncOpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=settings.GROQ_API_KEY,
            )

    async def score_papers(
        self, papers: list, profile: dict
    ) -> list[dict]:
        papers_data = [
            {
                "paper_id": str(p.id),
                "title": p.title,
                "abstract": (p.abstract or "")[:500],
                "authors": p.authors,
                "categories": p.categories,
            }
            for p in papers
        ]

        all_scores = []

        for i in range(0, len(papers_data), self.BATCH_SIZE):
            batch = papers_data[i : i + self.BATCH_SIZE]
            scores = await self._score_batch(batch, profile)
            all_scores.extend(scores)

        return all_scores

    async def _score_batch(
        self, papers_data: list[dict], profile: dict
    ) -> list[dict]:
        prompt = build_user_prompt(profile, papers_data)

        try:
            raw = await self.llm.generate_completion(
                system_prompt=SYSTEM_PROMPT,
                prompt=prompt,
                temperature=0.1,
                max_tokens=4096,
            )
            raw = raw.strip()
            raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            scores = json.loads(raw)
            if isinstance(scores, list):
                return scores
        except Exception as e:
            print(f"[DiscoveryAgent] LLMService scoring failed: {e}")

        if self._groq_client:
            try:
                raw = await self._score_with_groq(prompt)
                raw = raw.strip()
                raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                scores = json.loads(raw)
                if isinstance(scores, list):
                    return scores
            except Exception as e:
                print(f"[DiscoveryAgent] Groq scoring failed: {e}")

        return self._score_fallback(papers_data, profile)

    async def _score_with_groq(self, prompt: str) -> str:
        response = await self._groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=4096,
        )
        return response.choices[0].message.content

    def _score_fallback(
        self, papers_data: list[dict], profile: dict
    ) -> list[dict]:
        interests = [t.lower() for t in profile.get("topics", [])]
        categories = [c.lower() for c in profile.get("categories", [])]
        keywords = [k.lower() for k in profile.get("keywords", [])]

        results = []
        for paper in papers_data:
            score = 50
            reason = "General Discovery"

            paper_cats = [c.lower() for c in paper.get("categories", [])]
            cat_match = any(c in paper_cats for c in categories)
            text = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()
            kw_match = any(k in text for k in keywords)

            if cat_match:
                score += 25
                reason = "Interest Category Match"
            if kw_match:
                score += 20
                reason = "Keyword Match" if reason == "General Discovery" else f"{reason} + Keyword Match"

            results.append({
                "paper_id": paper["paper_id"],
                "score": min(score, 99),
                "reason": reason,
            })
        return results
