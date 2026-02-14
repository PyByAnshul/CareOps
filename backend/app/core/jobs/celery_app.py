import logging
import sys

from celery import Celery

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

celery_app = Celery(
    "careops",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.addons.automation.tasks",
        "app.addons.inbox.tasks",
        "app.addons.forms.tasks",
    ],
)

conf = {
    "task_serializer": "json",
    "accept_content": ["json"],
    "result_serializer": "json",
    "timezone": "UTC",
    "enable_utc": True,
    "task_track_started": True,
    "task_time_limit": 300,
}
# Soft time limits use SIGUSR1, which Windows doesn't support
if sys.platform != "win32":
    conf["task_soft_time_limit"] = 240

celery_app.conf.update(conf)

logger.info("Celery app configured")
