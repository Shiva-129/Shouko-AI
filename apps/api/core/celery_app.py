from celery import Celery
from core.config import settings

# Initialize Celery client
celery_app = Celery(
    "paperbrain_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Optional configuration overrides
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    imports=[
        "tasks.digest_tasks"
    ]
)
