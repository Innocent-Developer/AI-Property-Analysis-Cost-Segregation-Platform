from celery import Celery
from kombu import Queue

from app.config.settings import get_settings


settings = get_settings()

celery = Celery("property_analysis")
celery.conf.update(settings.celery_config())

# Explicit queues for different stages of the pipeline
celery.conf.task_queues = (
    Queue("image_processing"),
    Queue("ai_detection"),
    Queue("report_generation"),
)


@celery.task(name="workers.ping")
def ping() -> str:
    return "pong"


