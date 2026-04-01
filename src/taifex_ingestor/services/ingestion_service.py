"""Top-level ingestion orchestration service."""

from __future__ import annotations

import json
import logging

from taifex_ingestor.clients.gcs_uploader import GcsUploader
from taifex_ingestor.config import AppConfig
from taifex_ingestor.models import ParsedRecord
from taifex_ingestor.parsers.taifex_parser import TaifexParser
from taifex_ingestor.services.download_service import DownloadService

logger = logging.getLogger(__name__)


class IngestionService:
    """Coordinates download, parse, and optional upload workflow."""

    def __init__(
        self,
        config: AppConfig,
        download_service: DownloadService,
        parser: TaifexParser,
        uploader: GcsUploader | None = None,
    ) -> None:
        self.config = config
        self.download_service = download_service
        self.parser = parser
        self.uploader = uploader

    def run(self) -> dict[str, list[ParsedRecord]]:
        ingested: dict[str, list[ParsedRecord]] = {}
        for download in self.download_service.download_all():
            records = self.parser.parse(download.source, download.content)
            ingested[download.source.source_type.value] = records
            logger.info("Parsed %s records for %s", len(records), download.source.source_type)

            if self.uploader:
                payload = json.dumps([record.row for record in records], ensure_ascii=False)
                object_name = f"{download.source.source_type.value}.json"
                self.uploader.upload_text(object_name=object_name, data=payload)
                logger.info("Uploaded %s", object_name)

        return ingested
