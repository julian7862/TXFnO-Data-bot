"""Logging helpers for CLI and services."""

import logging


def configure_logging(level: int = logging.INFO) -> None:
    """Configure package-wide logging."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
