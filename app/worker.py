"""Celery application configuration"""

from celery import Celery
from celery.schedules import crontab

from app.config import settings

# Create Celery app
celery = Celery(
    "job_bot",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Configure Celery
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    worker_pool="solo",  # Use solo pool on Windows to avoid multiprocessing issues
)

# Define periodic tasks (will be added in Phase 2+)
celery.conf.beat_schedule = {
    # Uncomment in Phase 2 when scraper tasks are ready
    # "scrape-jobs-every-4-hours": {
    #     "task": "app.worker.tasks.run_all_scrapers",
    #     "schedule": crontab(minute=0, hour="*/4"),
    # },
    # "score-new-jobs-every-hour": {
    #     "task": "app.worker.tasks.score_new_jobs",
    #     "schedule": crontab(minute=0),
    # },
    # "check-gmail-every-2-hours": {
    #     "task": "app.worker.tasks.check_for_replies",
    #     "schedule": crontab(minute=0, hour="*/2"),
    # },
}


# Task autodiscovery
celery.autodiscover_tasks(["app"])


@celery.task(bind=True)
def debug_task(self):
    """Test task for debugging"""
    print(f"Request: {self.request!r}")
