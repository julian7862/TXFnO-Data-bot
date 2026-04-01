"""Logging helpers for the TXFnO data bot CLI."""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone


class StructuredFormatter(logging.Formatter):
    """Small structured formatter with human-readable key=value fields."""

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()
        message = record.getMessage().replace("\n", "\\n")
        fields = [
            f"ts={timestamp}",
            f"level={record.levelname}",
            f"logger={record.name}",
            f"msg={message}",
        ]

        if record.exc_info:
            fields.append(f"exc={self.formatException(record.exc_info).replace(chr(10), ' | ')}")

        for key, value in record.__dict__.items():
            if key in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "message",
                "asctime",
            }:
                continue
            fields.append(f"{key}={value}")

        return " ".join(fields)


def configure_logging(level: str = "INFO") -> None:
    """Configure root logging once for CLI usage."""

    root = logging.getLogger()
    root.handlers.clear()
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(StructuredFormatter())
    root.addHandler(handler)

    numeric_level = getattr(logging, level.upper(), logging.INFO)
    root.setLevel(numeric_level)
