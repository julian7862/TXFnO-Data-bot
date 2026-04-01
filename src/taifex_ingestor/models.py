"""Shared data models for source definitions and ingestion outputs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from taifex_ingestor.enums import SourceType


@dataclass(frozen=True)
class SourceDefinition:
    """Source metadata used by crawl/download/upload services."""

    name: str
    source_type: SourceType
    page_url: str


@dataclass(frozen=True)
class CrawlResult:
    """Downloadable artifact found from one TAIFEX listing page for a target date."""

    source: SourceDefinition
    trading_date: date
    csv_zip_url: str


@dataclass(frozen=True)
class DownloadResult:
    """Represents one downloaded ZIP file persisted locally."""

    source: SourceDefinition
    trading_date: date
    download_url: str
    local_path: Path


@dataclass(frozen=True)
class UploadResult:
    """Represents one uploaded object in cloud storage."""

    source: SourceDefinition
    trading_date: date
    object_name: str


@dataclass(frozen=True)
class IngestionResult:
    """One source end-to-end ingestion result."""

    source: SourceDefinition
    target_date: date
    status: str
    crawl: CrawlResult | None = None
    download: DownloadResult | None = None
    upload: UploadResult | None = None
