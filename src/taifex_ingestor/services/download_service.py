"""Download service for TAIFEX ZIP artifacts."""

from __future__ import annotations

import io
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from taifex_ingestor.clients.http_client import HttpClient
from taifex_ingestor.exceptions import DownloadError
from taifex_ingestor.models import CrawlResult, DownloadResult


class DownloadService:
    """Download and persist validated ZIP artifacts."""

    def __init__(self, http_client: HttpClient, output_dir: Path) -> None:
        self.http_client = http_client
        self.output_dir = output_dir

    def _build_destination(self, crawl: CrawlResult) -> Path:
        filename = f"{crawl.source.source_type.value}_{crawl.trading_date.strftime('%Y%m%d')}.csv.zip"
        return self.output_dir / crawl.source.source_type.value / crawl.trading_date.isoformat() / filename

    def download(self, crawl: CrawlResult) -> DownloadResult:
        payload = self.http_client.get_bytes(crawl.csv_zip_url)
        if not payload:
            raise DownloadError(f"Downloaded empty payload from {crawl.csv_zip_url}")

        try:
            with ZipFile(io.BytesIO(payload), "r") as zip_handle:
                if not zip_handle.namelist():
                    raise DownloadError(f"ZIP contains no entries: {crawl.csv_zip_url}")
        except BadZipFile as exc:
            raise DownloadError(f"Downloaded content is not a valid ZIP: {crawl.csv_zip_url}") from exc

        destination = self._build_destination(crawl)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload)

        return DownloadResult(
            source=crawl.source,
            trading_date=crawl.trading_date,
            download_url=crawl.csv_zip_url,
            local_path=destination,
        )
