"""Shared data models for source definitions and ingestion outputs."""

from dataclasses import dataclass

from taifex_ingestor.enums import SourceType


@dataclass(frozen=True)
class SourceDefinition:
    """Source metadata used by download/parsing services."""

    name: str
    source_type: SourceType
    url: str


@dataclass(frozen=True)
class DownloadResult:
    """Represents one downloaded payload from TAIFEX."""

    source: SourceDefinition
    content: bytes


@dataclass(frozen=True)
class ParsedRecord:
    """Simple parsed record container."""

    source_name: str
    row: dict[str, str]
