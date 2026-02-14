#!/usr/bin/env python
"""
Celery worker startup script.

Usage:
    python worker.py

Or with Celery CLI:
    celery -A app.core.jobs.celery_app worker --loglevel=info

On Windows use the solo pool to avoid billiard/multiprocessing issues:
    celery -A app.core.jobs.celery_app worker --loglevel=info --pool=solo
"""

import sys

from app.core.jobs.celery_app import celery_app

if __name__ == "__main__":
    args = [
        "worker",
        "--loglevel=info",
    ]
    if sys.platform == "win32":
        # Prefork pool (billiard) causes PermissionError / invalid handle on Windows.
        # Solo runs tasks in the main process; no multiprocessing.
        args.append("--pool=solo")
    else:
        args.append("--concurrency=2")
    celery_app.worker_main(args)
