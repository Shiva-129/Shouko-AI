import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.user import User
from models.paper import Paper
from models.digest import DailyDigest
from services.email_service import EmailService

class DigestService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.email_service = EmailService()

    async def compile_user_daily_digest(self, user_id, date: datetime.date) -> DailyDigest | None:
        """
        Retrieves recent papers, matches them against the user interest profile,
        compiles a DailyDigest and dispatches it via email.
        """
        # 1. Load user
        user_res = await self.db.execute(select(User).where(User.id == user_id))
        user = user_res.scalar_one_or_none()
        if not user:
            print(f"[DigestService] User {user_id} not found.")
            return None

        # 2. Query recent papers ingested in the last 48 hours
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(hours=48)
        papers_res = await self.db.execute(
            select(Paper).where(Paper.created_at >= cutoff)
        )
        papers = papers_res.scalars().all()
        if not papers:
            print("[DigestService] No recent papers ingested for recommendations.")
            return None

        # 3. Match interests
        profile = user.interest_profile or {}
        interests = [t.lower() for t in profile.get("topics", [])]
        categories = [c.lower() for c in profile.get("categories", [])]
        keywords = [k.lower() for k in profile.get("keywords", [])]

        paper_scores = []
        recommendations = []

        for paper in papers:
            score = 50  # Base score
            matched_reason = "General Discovery"

            # Check matches
            category_match = any(c in paper.category.lower() for c in categories) if paper.category else False
            title_text = f"{paper.title} {paper.abstract}".lower()
            keyword_match = any(k in title_text for k in keywords)

            if category_match:
                score += 25
                matched_reason = "Interest Category Match"
            if keyword_match:
                score += 20
                matched_reason = "Keyword Match"

            # Normalize to max 99
            score = min(score, 99)

            if score >= 60 or len(paper_scores) < 3:
                paper_scores.append({
                    "paper_id": str(paper.id),
                    "score": score,
                    "reason": matched_reason
                })
                recommendations.append({
                    "title": paper.title,
                    "abstract": paper.abstract or "No abstract provided.",
                    "category": paper.category or "General",
                    "match_score": score,
                    "url": f"http://localhost:3000/workspaces/{paper.id}"
                })

        if not paper_scores:
            print(f"[DigestService] No relevant papers matched user {user.email}'s interests today.")
            return None

        # 4. Check for existing daily digest to prevent duplicate sends
        existing_res = await self.db.execute(
            select(DailyDigest).where(
                DailyDigest.user_id == user.id,
                DailyDigest.date == date
            )
        )
        digest = existing_res.scalar_one_or_none()

        if not digest:
            digest = DailyDigest(
                user_id=user.id,
                date=date,
                paper_scores=paper_scores,
                paper_count=len(paper_scores),
                status="pending"
            )
            self.db.add(digest)
            await self.db.flush()

        # 5. Dispatch email
        email_sent = await self.email_service.send_digest(
            to_email=user.email,
            user_name=user.name or user.email.split("@")[0],
            recommendations=recommendations
        )

        if email_sent:
            digest.status = "sent"
            digest.email_sent_at = datetime.datetime.utcnow()
        else:
            digest.status = "ready"  # Ready to be retried later

        await self.db.commit()
        print(f"[DigestService] Digest generation & email pipeline finished with status: {digest.status}")
        return digest
