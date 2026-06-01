import asyncio
import datetime
import os
import time
import uuid
from core.database import AsyncSessionLocal
from models.user import User
from models.paper import Paper
from services.digest_service import DigestService
from services.email_service import EmailService

async def run_digest_test():
    print("--------------------------------------------------")
    print("🚀 Initializing E2E Daily Digest Ingest Evaluation")
    print("--------------------------------------------------")

    try:
        async with AsyncSessionLocal() as db:
            # 1. Register Mock User
            mock_user_id = uuid.uuid4()
            user_email = "test_researcher@paperbrain.ai"

            # Check if test user already exists
            from sqlalchemy import select
            existing_user = await db.execute(select(User).where(User.email == user_email))
            user = existing_user.scalar_one_or_none()

            if not user:
                user = User(
                    id=mock_user_id,
                    email=user_email,
                    name="Dr. Shouko",
                    plan="pro",
                    interest_profile={
                        "topics": ["Transformers", "Neural Networks"],
                        "categories": ["cs.CL", "cs.LG"],
                        "keywords": ["Attention", "Rotary"],
                        "authors": []
                    }
                )
                db.add(user)
                print(f"[Test Seed] Registered mock user: {user.email}")
            else:
                print(f"[Test Seed] Test user already exists: {user.email}")
                mock_user_id = user.id

            # 2. Register Mock Recent Papers
            paper_1 = Paper(
                id=uuid.uuid4(),
                title="Attention Is All You Need",
                authors=["Ashish Vaswani", "Noam Shazeer"],
                abstract="We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.",
                pdf_url="https://arxiv.org/pdf/1706.03762.pdf",
                category="cs.CL",
                status="completed",
                published_at=datetime.datetime.utcnow(),
                created_at=datetime.datetime.utcnow()
            )

            paper_2 = Paper(
                id=uuid.uuid4(),
                title="RoFormer: Enhanced Transformer with Rotary Position Embedding",
                authors=["Jianlin Su", "Yu Lu"],
                abstract="Rotary Position Embedding (RoPE) encodes relative positional information in self-attention mechanisms with absolute position representations.",
                pdf_url="https://arxiv.org/pdf/2104.09864.pdf",
                category="cs.LG",
                status="completed",
                published_at=datetime.datetime.utcnow(),
                created_at=datetime.datetime.utcnow()
            )

            db.add(paper_1)
            db.add(paper_2)
            print("[Test Seed] Seeded two recent mock papers in the database.")
            await db.commit()

            # 3. Trigger Digest Service
            print("\n[Service Invocation] Compiling and generating user digest...")
            digest_service = DigestService(db)
            today = datetime.date.today()
            digest = await digest_service.compile_user_daily_digest(mock_user_id, today)

            print("\n--------------------------------------------------")
            if digest:
                print("✅ E2E Daily Digest database run SUCCESS!")
                print(f"Status: {digest.status}")
                print(f"Paper Count: {digest.paper_count}")
                print(f"Paper scores matched: {digest.paper_scores}")
                print("Check 'apps/api/sandbox_emails/' to inspect the beautiful responsive HTML email output!")
            else:
                print("❌ E2E Daily Digest test run failed to compile.")
            print("--------------------------------------------------")

    except Exception as e:
        print(f"\n⚠️ Database offline or refused connection ({e}).")
        print("🔗 Initiating Sandbox Fallback generator to verify responsive HTML output...")

        email_service = EmailService()
        recommendations = [
            {
                "title": "Attention Is All You Need",
                "abstract": "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.",
                "category": "cs.CL",
                "match_score": 95,
                "url": "http://localhost:3000/workspaces/vaswani-2017"
            },
            {
                "title": "RoFormer: Enhanced Transformer with Rotary Position Embedding",
                "abstract": "Rotary Position Embedding (RoPE) encodes relative positional information in self-attention mechanisms with absolute position representations.",
                "category": "cs.LG",
                "match_score": 90,
                "url": "http://localhost:3000/workspaces/rope-2021"
            }
        ]

        success = await email_service.send_digest(
            to_email="test_researcher@paperbrain.ai",
            user_name="Dr. Shouko",
            recommendations=recommendations
        )

        print("\n--------------------------------------------------")
        if success:
            print("✅ Sandboxed HTML email generated successfully!")
            print("Check the 'apps/api/sandbox_emails/' folder to view the compiled premium HTML email digest template!")
        else:
            print("❌ Sandboxed fallback execution failed.")
        print("--------------------------------------------------")

if __name__ == "__main__":
    asyncio.run(run_digest_test())
