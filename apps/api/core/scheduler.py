import asyncio
import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.config import settings

scheduler = AsyncIOScheduler(timezone="UTC")


def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


async def daily_scan_job():
    from tasks.digest_tasks import async_scan_daily_research_papers
    from tasks.digest_tasks import async_compile_and_send_digests

    print("[Scheduler] Running daily ArXiv scan...")
    try:
        count = await async_scan_daily_research_papers()
        print(f"[Scheduler] Scan complete: {count} new papers.")
    except Exception as e:
        print(f"[Scheduler] Scan failed: {e}")

    print("[Scheduler] Running daily digest compilation...")
    try:
        sent = await async_compile_and_send_digests()
        print(f"[Scheduler] Digests sent: {sent}")
    except Exception as e:
        print(f"[Scheduler] Digests failed: {e}")


def start_scheduler():
    if settings.ENVIRONMENT == "development":
        print("[Scheduler] Dev mode — first scan in 10s, then every 24h.")
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
            run_date=datetime.datetime.utcnow() + datetime.timedelta(seconds=10),
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
    print("[Scheduler] APScheduler started.")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("[Scheduler] APScheduler stopped.")
