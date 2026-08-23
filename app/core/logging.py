"""AMIP logging configuration.

Console output is concise for operators; rotating files keep diagnostic detail
and contextual identifiers for support. Sensitive values are redacted before
any formatted record reaches disk or the terminal.
"""

from __future__ import annotations

import logging
import os
import re
import sys
import threading
from contextlib import contextmanager
from contextvars import ContextVar
from logging.handlers import RotatingFileHandler
from typing import Iterator, Optional

from app.config import settings

_LOG_CONTEXT: ContextVar[dict[str, object]] = ContextVar("amip_log_context", default={})
_CONTEXT_FIELDS = (
    "request_id",
    "meeting_id",
    "job_id",
    "job_type",
    "attempt",
    "worker_id",
    "error_code",
)
_SECRET_ENV_MARKERS = ("SECRET", "TOKEN", "PASSWORD", "API_KEY", "PRIVATE_KEY", "ACCESS_KEY")


class SensitiveDataRedactor:
    """Best-effort redaction for credentials that could leak through errors."""

    _assignment_pattern = re.compile(
        r"(?i)\b(secret(?:_key)?|token|password|api[_-]?key|authorization)\b"
        r"(\s*[:=]\s*)([^\s,;]+)"
    )
    _bearer_pattern = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+")
    _url_credentials_pattern = re.compile(
        r"(?P<scheme>[a-zA-Z][a-zA-Z0-9+.-]*://)[^/@\s:]+:[^/@\s]+@"
    )

    @classmethod
    def _known_values(cls) -> tuple[str, ...]:
        values: list[str] = []
        for key, value in os.environ.items():
            if value and len(value) >= 6 and any(
                marker in key.upper() for marker in _SECRET_ENV_MARKERS
            ):
                values.append(value)
        return tuple(sorted(set(values), key=len, reverse=True))

    @classmethod
    def redact(cls, text: str) -> str:
        sanitized = text
        for value in cls._known_values():
            sanitized = sanitized.replace(value, "[REDACTED]")
        sanitized = cls._bearer_pattern.sub("Bearer [REDACTED]", sanitized)
        sanitized = cls._assignment_pattern.sub(r"\1\2[REDACTED]", sanitized)
        sanitized = cls._url_credentials_pattern.sub(r"\g<scheme>[REDACTED]@", sanitized)
        return sanitized


@contextmanager
def log_context(**values: object) -> Iterator[None]:
    """Temporarily enrich every log record in the current execution context."""
    merged = dict(_LOG_CONTEXT.get())
    merged.update({key: value for key, value in values.items() if value is not None})
    token = _LOG_CONTEXT.set(merged)
    try:
        yield
    finally:
        _LOG_CONTEXT.reset(token)


class DiagnosticContextFilter(logging.Filter):
    """Guarantee stable context fields for technical log formatting."""

    def filter(self, record: logging.LogRecord) -> bool:
        current = _LOG_CONTEXT.get()
        for field in _CONTEXT_FIELDS:
            if not hasattr(record, field):
                setattr(record, field, current.get(field, "-"))
        return True


class RedactingTechnicalFormatter(logging.Formatter):
    """Format full technical records, then redact final text including traceback."""

    def format(self, record: logging.LogRecord) -> str:
        return SensitiveDataRedactor.redact(super().format(record))


class FriendlyConsoleFormatter(logging.Formatter):
    _prefixes = {
        logging.DEBUG: "·",
        logging.INFO: "✓",
        logging.WARNING: "⚠",
        logging.ERROR: "✗",
        logging.CRITICAL: "✗",
    }

    def format(self, record: logging.LogRecord) -> str:
        message = SensitiveDataRedactor.redact(record.getMessage())
        error_code = getattr(record, "error_code", None)
        code_suffix = f" [{error_code}]" if error_code and error_code != "-" else ""
        return f"{self._prefixes.get(record.levelno, '→')} {message}{code_suffix}"


class LoggerFactory:
    """Create consistent AMIP and root log handlers."""

    _file_formatter = RedactingTechnicalFormatter(
        "%(asctime)s | %(levelname)s | %(name)s | pid=%(process)d | thread=%(threadName)s | "
        "request_id=%(request_id)s | meeting_id=%(meeting_id)s | job_id=%(job_id)s | "
        "job_type=%(job_type)s | attempt=%(attempt)s | worker_id=%(worker_id)s | "
        "error_code=%(error_code)s | %(pathname)s:%(lineno)d | %(funcName)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    _console_formatter = FriendlyConsoleFormatter()
    _context_filter = DiagnosticContextFilter()

    @classmethod
    def _level(cls, level: Optional[str]) -> int:
        value = level or settings.logging.LOG_LEVEL
        return getattr(logging, value.upper(), logging.INFO)

    @classmethod
    def _create_console_handler(cls) -> logging.StreamHandler:
        handler = logging.StreamHandler(sys.stdout)
        handler.addFilter(cls._context_filter)
        handler.setFormatter(cls._console_formatter)
        return handler

    @classmethod
    def _create_file_handler(cls) -> RotatingFileHandler:
        log_dir = os.path.dirname(settings.logging.LOG_FILE)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        handler = RotatingFileHandler(
            settings.logging.LOG_FILE,
            maxBytes=settings.logging.LOG_MAX_BYTES,
            backupCount=settings.logging.LOG_BACKUP_COUNT,
            encoding="utf-8",
            delay=True,
        )
        handler.addFilter(cls._context_filter)
        handler.setFormatter(cls._file_formatter)
        return handler

    @classmethod
    def configure_root(cls, level: Optional[str] = None) -> logging.Logger:
        root = logging.getLogger()
        root.setLevel(cls._level(level))
        root.handlers.clear()
        root.addHandler(cls._create_console_handler())
        root.addHandler(cls._create_file_handler())
        return root

    @classmethod
    def get_logger(
        cls,
        name: str,
        level: Optional[str] = None,
        console: bool = True,
        file: bool = True,
    ) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(cls._level(level))
        logger.handlers.clear()
        logger.propagate = False
        if console:
            logger.addHandler(cls._create_console_handler())
        if file:
            logger.addHandler(cls._create_file_handler())
        return logger


def _install_uncaught_exception_hooks() -> None:
    def handle_main(exc_type, exc_value, exc_traceback) -> None:  # type: ignore[no-untyped-def]
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.getLogger("amip.uncaught").critical(
            "Unhandled application exception",
            exc_info=(exc_type, exc_value, exc_traceback),
            extra={"error_code": "AMIP-001"},
        )

    def handle_thread(args: threading.ExceptHookArgs) -> None:
        logging.getLogger("amip.uncaught.thread").critical(
            "Unhandled exception in thread %s",
            args.thread.name if args.thread else "unknown",
            exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
            extra={"error_code": "AMIP-001"},
        )

    sys.excepthook = handle_main
    threading.excepthook = handle_thread


def setup_logging() -> logging.Logger:
    LoggerFactory.configure_root(settings.logging.LOG_LEVEL)
    main_logger = LoggerFactory.get_logger(
        "amip", level=settings.logging.LOG_LEVEL, console=True, file=True
    )
    _install_uncaught_exception_hooks()
    return main_logger


logger = setup_logging()
