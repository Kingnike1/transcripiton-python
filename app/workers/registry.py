"""Worker composition root.

Concrete job handlers are registered here by the Sprint that implements them.
The durable worker can exist before a transcription provider without consuming
unsupported jobs.
"""

from app.workers.job_worker import JobWorker


def build_worker() -> JobWorker:
    """Build the worker with currently available handlers."""
    return JobWorker()
