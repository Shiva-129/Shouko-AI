import asyncio
import datetime
import uuid
from sqlalchemy import select
from core.database import AsyncSessionLocal
from models.user import User
from models.paper import Paper
from models.artifact import Artifact
from tasks.generate_artifact import _run_generation

async def test_artifact_generation():
    print("--------------------------------------------------")
    print("🚀 Initializing Artifact Generation & Agent Evaluation")
    print("--------------------------------------------------")

    async with AsyncSessionLocal() as db:
        # 1. Retrieve or seed mock user
        user_email = "mock@paperbrain.app"
        user_res = await db.execute(select(User).where(User.email == user_email))
        user = user_res.scalar_one_or_none()
        
        if not user:
            user = User(
                id=uuid.uuid4(),
                email=user_email,
                name="Dr. Shouko",
                plan="pro",
                interest_profile={"topics": ["Transformers"], "categories": ["cs.CL"], "keywords": ["Attention"], "authors": []}
            )
            db.add(user)
            await db.flush()
            print(f"[Test Seed] Created mock user: {user.email}")
        else:
            print(f"[Test Seed] Mock user already exists: {user.email}")
            
        user_id = user.id

        # 2. Retrieve or seed mock paper (Attention Is All You Need)
        paper_url = "https://arxiv.org/pdf/1706.03762.pdf"
        paper_res = await db.execute(select(Paper).where(Paper.pdf_url == paper_url))
        papers = list(paper_res.scalars().all())
        
        if not papers:
            paper = Paper(
                id=uuid.uuid4(),
                title="Attention Is All You Need",
                authors=["Ashish Vaswani", "Noam Shazeer"],
                abstract="We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.",
                pdf_url=paper_url,
                categories=["cs.CL"],
                published_date=datetime.date.today(),
                source="arxiv",
                pdf_processed=False
            )
            db.add(paper)
            await db.flush()
            print(f"[Test Seed] Created mock paper: {paper.title}")
        else:
            paper = papers[0]
            print(f"[Test Seed] Mock paper already exists: {paper.title}")
            
        paper_id = paper.id

        # 3. Check if artifact already exists, delete it for a clean test run
        existing_artifact_res = await db.execute(
            select(Artifact).where(Artifact.user_id == user_id, Artifact.paper_id == paper_id)
        )
        existing_artifacts = list(existing_artifact_res.scalars().all())
        for existing_artifact in existing_artifacts:
            print("[Test Seed] Deleting existing artifact for a clean run.")
            await db.delete(existing_artifact)
        if existing_artifacts:
            await db.commit()

        # 4. Create new Artifact record (queued)
        artifact = Artifact(
            id=uuid.uuid4(),
            user_id=user_id,
            paper_id=paper_id,
            status="queued"
        )
        db.add(artifact)
        await db.commit()
        artifact_id = artifact.id
        print(f"[Artifact Flow] Created queued artifact: {artifact_id}")

        # 5. Trigger the generation task directly (async)
        print("\n[Service Invocation] Running generation task (Ingestion + Generation)...")
        await _run_generation(str(paper_id), str(artifact_id), str(user_id))

        # 6. Retrieve and check results
        await db.refresh(artifact)
        print("\n--------------------------------------------------")
        print("🔍 Artifact Generation Results:")
        print(f"Status: {artifact.status}")
        print(f"Error Message: {artifact.error_message}")
        print(f"One Line Summary: {artifact.one_line_summary}")
        
        if artifact.status == "ready":
            print("✅ Artifact generation task SUCCESS!")
            print(f"Summary Length: {len(artifact.summary) if artifact.summary else 0} characters")
            print(f"Key Insights Count: {len(artifact.key_insights)}")
            print(f"Auto QA Count: {len(artifact.auto_qa)}")
            print(f"Suggested Experiments Count: {len(artifact.suggested_experiments)}")
            
            # Print samples
            if artifact.key_insights:
                print(f"\nSample Insight: {artifact.key_insights[0]}")
            if artifact.auto_qa:
                print(f"Sample QA Pair: {artifact.auto_qa[0]}")
            if artifact.suggested_experiments:
                print(f"Sample Experiment: {artifact.suggested_experiments[0]}")
        else:
            print("❌ Artifact generation task FAILED.")
        print("--------------------------------------------------")

if __name__ == "__main__":
    asyncio.run(test_artifact_generation())
