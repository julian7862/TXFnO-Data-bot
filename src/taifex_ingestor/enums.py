"""Enum declarations used across ingestion components."""

from enum import Enum


class SourceType(str, Enum):
    """Supported market data source types."""

    FUTURES = "futures"
    OPTIONS = "options"
