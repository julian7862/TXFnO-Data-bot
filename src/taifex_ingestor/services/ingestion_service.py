"""Top-level ingestion orchestration service."""

from __future__ import annotations

import logging
from datetime import date

from taifex_ingestor.clients.gcs_uploader import GcsUploader
from taifex_ingestor.clients.http_client import HttpClient
from taifex_ingestor.config import AppConfig
from taifex_ingestor.enums import SourceType
from taifex_ingestor.models import IngestionResult
from taifex_ingestor.parsers.taifex_parser import TaifexParser
from taifex_ingestor.services.download_service import DownloadService
from taifex_ingestor.sources.definitions import build_source_definitions

logger = logging.getLogger(__name__)


class IngestionService:
    """Coordinates crawl, parse, download, and optional upload."""

    def __init__(
        self,
        config: AppConfig,
        http_client: HttpClient,
        parser: TaifexParser,
        download_service: DownloadService,
        uploader: GcsUploader | None,
    ) -> None:
        self.config = config
        self.http_client = http_client
        self.parser = parser
        self.download_service = download_service
        self.uploader = uploader
        self.sources = build_source_definitions(config)

    def run_source(self, source_type: SourceType, target_date: date) -> IngestionResult:
        source = self.sources[source_type]
        html = self.http_client.get_text(source.page_url)
        crawl = self.parser.find_for_date(source, html, target_date)

        if crawl is None:
            logger.info(
                "No CSV ZIP for target date; likely non-trading day or file not published yet. source=%s date=%s",
                source_type.value,
                target_date.isoformat(),
            )
            return IngestionResult(
                source=source,
                target_date=target_date,
                status="no_file_for_today",
            )

        download = self.download_service.download(crawl)
        upload = self.uploader.upload_file(download) if self.uploader else None

        logger.info(
            "ingested source=%s date=%s url=%s local=%s uploaded=%s",
            source_type.value,
            crawl.trading_date.isoformat(),
            crawl.csv_zip_url,
            download.local_path,
            f"gs://{self.config.gcs_bucket}/{upload.object_name}" if upload and self.config.gcs_bucket else None,
        )
        return IngestionResult(
            source=source,
            target_date=target_date,
            status="downloaded",
            crawl=crawl,
            download=download,
            upload=upload,
        )

    def run(self, target: str = "all", target_date: date | None = None) -> dict[str, IngestionResult]:
        run_date = target_date or date.today()

        targets: list[SourceType]
        if target == "all":
            targets = [SourceType.FUTURES, SourceType.OPTIONS]
        else:
            targets = [SourceType(target)]

        results: dict[str, IngestionResult] = {}
        for source_type in targets:
            results[source_type.value] = self.run_source(source_type, run_date)
        return results
