from app.core.config import settings

try:
    from celery import Celery
except ImportError:
    Celery = None  # type: ignore[assignment]

class _UnavailableTask:
    def __init__(self, func): self.func = func
    def __call__(self, *args, **kwargs): return self.func(*args, **kwargs)
    def delay(self, *args, **kwargs): raise RuntimeError("Celery is not installed or configured")

class _FallbackCelery:
    def task(self, *args, **kwargs):
        def decorator(func): return _UnavailableTask(func)
        return decorator
    def autodiscover_tasks(self, packages): return None

if Celery is None:
    celery_app = _FallbackCelery()
else:
    celery_app = Celery("openresearch", broker=settings.redis_url, backend=settings.redis_url)
    celery_app.conf.update(task_track_started=True, task_serializer="json", result_serializer="json", accept_content=["json"])
    celery_app.autodiscover_tasks(["app.tasks"])
