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

# Fault tolerance: retries and ack behavior
celery.conf.task_acks_late = True
celery.conf.task_reject_on_worker_lost = True
celery.conf.task_default_retry_delay = 60
celery.conf.task_max_retries = 3
celery.conf.task_serializer = "json"
celery.conf.result_serializer = "json"


@celery.task(name="workers.ping")
def ping() -> str:
    return "pong"


