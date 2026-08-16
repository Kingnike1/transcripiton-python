"""Standalone AMIP background worker entrypoint."""

from app.core.logging import logger
from app.workers.registry import build_worker


def main() -> None:
    worker = build_worker()
    logger.info("Starting AMIP background worker")
    worker.run_forever()


if __name__ == "__main__":
    main()
