"""Executable entrypoint for the durable AMIP worker."""

from app.core.logging import logger
from app.workers.registry import build_worker


def main() -> None:
    """Build configured handlers and process durable jobs forever."""
    worker = build_worker()
    logger.info("Starting durable AMIP worker")
    worker.run_forever()


if __name__ == "__main__":
    main()
