"""Executable entrypoint for the durable AMIP worker."""

from threading import Event, Thread

from app.core.logging import logger
from app.services.worker_heartbeat import WorkerHeartbeat
from app.workers.registry import build_worker


def _start_process_heartbeat(interval_seconds: float = 5.0) -> tuple[Event, Thread]:
    """Publish worker liveness even while a long-running job is executing."""
    stop = Event()
    heartbeat = WorkerHeartbeat()

    def loop() -> None:
        while not stop.is_set():
            try:
                heartbeat.touch()
            except OSError:
                logger.exception("Unable to publish worker heartbeat")
            stop.wait(interval_seconds)

    thread = Thread(target=loop, name="worker-process-heartbeat", daemon=True)
    thread.start()
    return stop, thread


def main() -> None:
    """Build configured handlers and process durable jobs forever."""
    worker = build_worker()
    heartbeat_stop, heartbeat_thread = _start_process_heartbeat()
    logger.info("Starting durable AMIP worker")
    try:
        worker.run_forever()
    finally:
        heartbeat_stop.set()
        heartbeat_thread.join(timeout=2)


if __name__ == "__main__":
    main()
