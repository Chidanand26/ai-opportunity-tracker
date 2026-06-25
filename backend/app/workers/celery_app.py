from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "ai_opportunity_tracker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        # Task modules are registered here as they are added:
        # "app.workers.tasks.scrape",
        # "app.workers.tasks.enrich",
        # "app.workers.tasks.notify",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    # Prevent tasks from running indefinitely
    task_soft_time_limit=300,   # 5 min — raises SoftTimeLimitExceeded
    task_time_limit=360,        # 6 min — hard kill
    # Retry failed tasks with exponential backoff
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)
