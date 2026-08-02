"""Background task definitions executed by Celery workers."""

from app.tasks import document_tasks  # noqa: F401 — registers Celery tasks on import
