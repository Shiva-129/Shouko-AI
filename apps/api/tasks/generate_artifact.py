import asyncio
import uuid
from sqlalchemy import select
from core.celery_app import celery_app
from core.database import AsyncSessionLocal
from core.usage import log_usage_event
from models.artifact import Artifact
from models.paper import Paper
from services.ingestion_service import IngestionService
from agents.artifact_agent import ArtifactAgent


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def generate_artifact(self, paper_id: str, artifact_id: str, user_id: str):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(
        _run_generation(paper_id, artifact_id, user_id)
    )


async def _run_generation(paper_id: str, artifact_id: str, user_id: str):
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(Artifact).where(Artifact.id == artifact_id))
            artifact = result.scalar_one_or_none()
            if not artifact:
                print(f"[GenerateArtifact] Artifact {artifact_id} not found")
                return

            artifact.status = "ingesting"
            await db.flush()

            result = await db.execute(select(Paper).where(Paper.id == paper_id))
            paper = result.scalar_one_or_none()

            if not paper:
                artifact.status = "failed"
                artifact.error_message = "Paper not found"
                await db.commit()
                return

            if not paper.pdf_processed:
                ingestion = IngestionService()
                await ingestion.ingest_paper(db, paper_id, paper.pdf_url)

            artifact.status = "generating"
            await db.flush()

            agent = ArtifactAgent(db)
            output = await agent.generate(paper_id, artifact_id)

            if output:
                artifact.status = "ready"
            else:
                artifact.status = "failed"
                if not artifact.error_message:
                    artifact.error_message = "Generation returned no output"

            await log_usage_event(db, user_id, "artifact_created", {
                "artifact_id": artifact_id,
                "paper_id": paper_id,
            })
            await db.commit()

        except Exception as e:
            await db.rollback()
            result = await db.execute(select(Artifact).where(Artifact.id == artifact_id))
            artifact = result.scalar_one_or_none()
            if artifact:
                artifact.status = "failed"
                artifact.error_message = str(e)
                await db.commit()
            print(f"[GenerateArtifact] Failed: {e}")
            raise
