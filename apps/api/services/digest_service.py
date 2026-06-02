import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.user import User
from models.paper import Paper
from models.digest import DailyDigest
from services.email_service import EmailService
from agents.discovery_agent import DiscoveryAgent


class DigestService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.email_service = EmailService()
        self.discovery_agent = DiscoveryAgent(db)

    async def compile_user_daily_digest(
        self, user_id, date: datetime.date
    ) -> DailyDigest | None:
        user_res = await self.db.execute(select(User).where(User.id == user_id))
        user = user_res.scalar_one_or_none()
        if not user:
            print(f"[DigestService] User {user_id} not found.")
            return None

        cutoff = datetime.datetime.utcnow() - datetime.timedelta(hours=48)
        papers_res = await self.db.execute(
            select(Paper).where(Paper.created_at >= cutoff)
        )
        papers = papers_res.scalars().all()
        if not papers:
            print("[DigestService] No recent papers.")
            return None

        profile = user.interest_profile or {}

        paper_scores = await self.discovery_agent.score_papers(papers, profile)

        if not paper_scores:
            paper_scores = self.discovery_agent._score_fallback(
                [
                    {
                        "paper_id": str(p.id),
                        "title": p.title,
                        "abstract": (p.abstract or "")[:500],
                        "authors": p.authors,
                        "categories": p.categories,
                    }
                    for p in papers
                ],
                profile,
            )

        min_score = 50
        scored_ids = {s["paper_id"] for s in paper_scores if s["score"] >= min_score}
        paper_map = {str(p.id): p for p in papers}

        filtered = [s for s in paper_scores if s["paper_id"] in scored_ids]
        filtered.sort(key=lambda x: x["score"], reverse=True)

        if not filtered:
            print(f"[DigestService] No papers scored >= {min_score} for {user.email}.")
            return None

        recommendations = []
        for s in filtered:
            p = paper_map.get(s["paper_id"])
            if p:
                recommendations.append({
                    "title": p.title,
                    "abstract": p.abstract or "No abstract provided.",
                    "category": p.categories[0] if p.categories else "General",
                    "match_score": s["score"],
                    "reason": s.get("reason", ""),
                    "paper_id": s["paper_id"],
                })

        existing_res = await self.db.execute(
            select(DailyDigest).where(
                DailyDigest.user_id == user.id,
                DailyDigest.date == date,
            )
        )
        digest = existing_res.scalar_one_or_none()

        if not digest:
            digest = DailyDigest(
                user_id=user.id,
                date=date,
                paper_scores=filtered,
                paper_count=len(filtered),
                status="pending",
            )
            self.db.add(digest)
            await self.db.flush()

        email_sent = await self.email_service.send_digest(
            to_email=user.email,
            user_name=user.name or user.email.split("@")[0],
            recommendations=recommendations,
        )

        if email_sent:
            digest.status = "sent"
            digest.email_sent_at = datetime.datetime.utcnow()
        else:
            digest.status = "ready"

        await self.db.commit()
        return digest
