from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date

from download_service import DownloadError, DownloadResult, DownloadService
from gcs_uploader import GCSUploader, UploadError, UploadResult

LOGGER = logging.getLogger(__name__)


class IngestionError(RuntimeError):
    """Raised for source-level ingestion failures."""


@dataclass(frozen=True)
class DownloadJob:
    source: str
    trade_date: date
    url: str
    filename: str


class SourceAdapter:
    """Adapter contract for fetch + parse steps per source."""

    def fetch(self, trade_date: date) -> object:
        raise NotImplementedError

    def parse(self, fetched: object, trade_date: date) -> list[DownloadJob]:
        raise NotImplementedError


@dataclass(frozen=True)
class IngestionRecord:
    download: DownloadResult
    upload: UploadResult


class IngestionService:
    """Orchestrates fetch → parse → download → upload for one or all sources."""

    def __init__(
        self,
        *,
        adapters: dict[str, SourceAdapter],
        downloader: DownloadService,
        uploader: GCSUploader,
    ) -> None:
        self.adapters = adapters
        self.downloader = downloader
        self.uploader = uploader

    def ingest_source(self, source: str, trade_date: date) -> list[IngestionRecord]:
        adapter = self.adapters.get(source)
        if adapter is None:
            raise IngestionError(f"Unknown source: {source}")

        try:
            fetched = adapter.fetch(trade_date)
            jobs = adapter.parse(fetched, trade_date)
        except Exception as exc:
            raise IngestionError(
                f"Failed during fetch/parse for source={source} date={trade_date.isoformat()}: {exc}"
            ) from exc

        records: list[IngestionRecord] = []

        for job in jobs:
            LOGGER.info(
                "ingestion_job_started",
                extra={
                    "source": source,
                    "date": trade_date.isoformat(),
                    "url": job.url,
                },
            )
            try:
                download = self.downloader.download_zip(
                    source=job.source,
                    trade_date=job.trade_date,
                    url=job.url,
                    filename=job.filename,
                )
                upload = self.uploader.upload_zip(
                    source=job.source,
                    trade_date=job.trade_date,
                    filename=job.filename,
                    local_path=download.local_path,
                )
            except (DownloadError, UploadError) as exc:
                raise IngestionError(
                    "Ingestion failed "
                    f"source={job.source} date={job.trade_date.isoformat()} "
                    f"url={job.url}: {exc}"
                ) from exc

            LOGGER.info(
                "ingestion_job_completed",
                extra={
                    "source": source,
                    "date": trade_date.isoformat(),
                    "url": job.url,
                    "local_path": str(download.local_path),
                    "gcs_object": upload.gcs_object,
                },
            )
            records.append(IngestionRecord(download=download, upload=upload))

        return records

    def ingest_all(self, trade_date: date) -> dict[str, list[IngestionRecord]]:
        results: dict[str, list[IngestionRecord]] = {}
        for source in self.adapters:
            results[source] = self.ingest_source(source, trade_date)
        return results
