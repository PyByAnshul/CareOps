import logging
from typing import Any

from celery import Task

logger = logging.getLogger(__name__)


class BaseTask(Task):
    """
    Base task class with standard logging and exception handling.
    """
    
    def on_success(self, retval: Any, task_id: str, args: tuple, kwargs: dict) -> None:
        """Called when task succeeds."""
        logger.info(f"Task {self.name} [{task_id}] succeeded", extra={
            "task_id": task_id,
            "task_name": self.name,
            "result": retval,
        })
    
    def on_failure(self, exc: Exception, task_id: str, args: tuple, kwargs: dict, einfo) -> None:
        """Called when task fails."""
        logger.error(f"Task {self.name} [{task_id}] failed: {str(exc)}", extra={
            "task_id": task_id,
            "task_name": self.name,
            "error": str(exc),
        })
    
    def on_retry(self, exc: Exception, task_id: str, args: tuple, kwargs: dict, einfo) -> None:
        """Called when task is retried."""
        logger.warning(f"Task {self.name} [{task_id}] retrying: {str(exc)}", extra={
            "task_id": task_id,
            "task_name": self.name,
            "error": str(exc),
        })
