import logging
import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from core.config import settings
from sqlalchemy import create_engine

logger = logging.getLogger("core.scheduler")



def _create_job_store():
    if settings.DATABASE_URL:
        sync_url = settings.DATABASE_URL.replace("+asyncpg", "")
        sync_engine = create_engine(sync_url, pool_pre_ping=True)
        return SQLAlchemyJobStore(engine=sync_engine)
    return None


scheduler = AsyncIOScheduler(
    timezone="UTC",
    jobstores={"default": _create_job_store()} if settings.DATABASE_URL else {},
)

async def daily_scan_job():
    from tasks.digest_tasks import async_scan_daily_research_papers
    from tasks.digest_tasks import async_compile_and_send_digests
    logger.info("[Scheduler] Running daily ArXiv scan...")
    try:
        count = await async_scan_daily_research_papers()
        logger.info(f"[Scheduler] Scan complete: {count} new papers.")
    except Exception as e:
        logger.info(f"[Scheduler] Scan failed: {e}")
    logger.info("[Scheduler] Running daily digest compilation...")
    try:
        sent = await async_compile_and_send_digests()
        logger.info(f"[Scheduler] Digests sent: {sent}")
    except Exception as e:
        logger.info(f"[Scheduler] Digests failed: {e}")


def start_scheduler():
    if settings.ENVIRONMENT == "development":
        logger.info("[Scheduler] Dev mode — first scan in 10s, then every 24h.")
        scheduler.add_job(
            daily_scan_job,
            trigger="interval",
            hours=24,
            id="daily_digest",
            replace_existing=True,
        )
        scheduler.add_job(
            daily_scan_job,
            trigger="date",
            run_date=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=10),
            id="daily_digest_bootstrap",
        )
    else:
        scheduler.add_job(
            daily_scan_job,
            trigger="cron",
            hour=6,
            minute=0,
            id="daily_digest",
            replace_existing=True,
        )

    scheduler.start()
    logger.info("[Scheduler] APScheduler started.")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("[Scheduler] APScheduler stopped.")
