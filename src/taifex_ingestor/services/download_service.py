"""Download service using shared source definitions."""

from taifex_ingestor.clients.http_client import HttpClient
from taifex_ingestor.models import DownloadResult
from taifex_ingestor.sources.definitions import SOURCE_DEFINITIONS


class DownloadService:
    """Download TAIFEX payloads for all defined source types."""

    def __init__(self, http_client: HttpClient) -> None:
        self.http_client = http_client

    def download_all(self) -> list[DownloadResult]:
        results: list[DownloadResult] = []
        for source in SOURCE_DEFINITIONS.values():
            content = self.http_client.get(source.url)
            results.append(DownloadResult(source=source, content=content))
        return results
