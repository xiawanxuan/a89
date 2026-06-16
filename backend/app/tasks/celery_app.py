from celery import Celery
from app.config import settings

celery_app = Celery(
    "yiman_repair",
    broker=settings.CELERY_BROKER_URL,
    backend="db+" + settings.DATABASE_URL_SYNC,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

celery_app.autodiscover_tasks(["app.tasks"])
