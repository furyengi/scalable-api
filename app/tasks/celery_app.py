from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "scalable_api",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.email_tasks", "app.tasks.report_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "app.tasks.email_tasks.*": {"queue": "email"},
        "app.tasks.report_tasks.*": {"queue": "reports"},
    },
    beat_schedule={
        "archive-old-tasks": {
            "task": "app.tasks.report_tasks.archive_old_tasks",
            "schedule": 86400,
        },
    },
)


@celery_app.task(name="app.tasks.notify", bind=True, max_retries=3)
def send_task_notification(self, user_id: int, task_id: int, event: str):
    try:
        print(f"📧 Notification: user={user_id}, task={task_id}, event={event}")
        return {"status": "sent", "task_id": task_id}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
