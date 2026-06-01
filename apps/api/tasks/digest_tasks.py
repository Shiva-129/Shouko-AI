import asyncio
import datetime
import arxiv
from celery import shared_task
from core.celery_app import celery_app
from core.database import AsyncSessionLocal
from sqlalchemy import select
from models.user import User
from models.paper import Paper
from services.digest_service import DigestService
from services.ingestion_service import IngestionService

def run_async(coro):
    """
    Helper to execute async coroutines from synchronous Celery workers.
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

@celery_app.task(name="tasks.scan_daily_research_papers")
def scan_daily_research_papers():
    """
    Scans the ArXiv API for newly published papers matching active user interest profiles
    and registers them inside the database.
    """
    return run_async(async_scan_daily_research_papers())

async def async_scan_daily_research_papers():
    print("[Celery Task] Running daily research scan...")
    async with AsyncSessionLocal() as db:
        # 1. Fetch active categories from all users
        res = await db.execute(select(User))
        users = res.scalars().all()
        categories = set()
        for user in users:
            profile = user.interest_profile or {}
            for cat in profile.get("categories", []):
                categories.add(cat.strip())

        if not categories:
            categories = {"cs.CL", "cs.LG", "cs.AI"}  # Standard fallback defaults

        # 2. Build query
        query_str = " OR ".join([f"cat:{c}" for c in categories])
        print(f"[Celery Task] Dispatching ArXiv search query: {query_str}")

        client = arxiv.Client()
        search = arxiv.Search(
            query=query_str,
            max_results=5,
            sort_by=arxiv.SortBy.SubmittedDate
        )

        ingested_count = 0
        try:
            for result in client.results(search):
                # Check if paper already exists
                existing_res = await db.execute(
                    select(Paper).where(Paper.title == result.title)
                )
                if existing_res.scalar_one_or_none():
                    continue

                # Register new metadata record
                paper = Paper(
                    title=result.title,
                    authors=[a.name for a in result.authors],
                    abstract=result.summary,
                    pdf_url=result.pdf_url,
                    category=result.primary_category,
                    published_at=result.published,
                    status="completed"  # Pre-compiled abstract ingest
                )
                db.add(paper)
                ingested_count += 1

            await db.commit()
            print(f"[Celery Task] Research scan complete. Successfully registered {ingested_count} new academic papers.")
            return ingested_count
        except Exception as e:
            print(f"[Celery Task] Error running daily research scan: {e}")
            return 0


@celery_app.task(name="tasks.compile_and_send_digests")
def compile_and_send_digests():
    """
    Compiles matching DailyDigests and dispatches emails for all active users.
    """
    return run_async(async_compile_and_send_digests())

async def async_compile_and_send_digests():
    print("[Celery Task] Compiling and sending user digests...")
    today = datetime.date.today()
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(User))
        users = res.scalars().all()
        if not users:
            print("[Celery Task] No users registered in database.")
            return 0

        digest_service = DigestService(db)
        sent_count = 0

        for user in users:
            try:
                digest = await digest_service.compile_user_daily_digest(user.id, today)
                if digest and digest.status == "sent":
                    sent_count += 1
            except Exception as e:
                print(f"[Celery Task] Failed compile for user {user.email}: {e}")

        print(f"[Celery Task] Daily digest execution complete. Sent out {sent_count} user digests.")
        return sent_count
