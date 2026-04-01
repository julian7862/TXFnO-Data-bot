"""CLI entrypoint for TAIFEX ingestor."""

from taifex_ingestor.clients.gcs_uploader import GcsUploader
from taifex_ingestor.clients.http_client import HttpClient
from taifex_ingestor.config import AppConfig
from taifex_ingestor.logging_config import configure_logging
from taifex_ingestor.parsers.taifex_parser import TaifexParser
from taifex_ingestor.services.download_service import DownloadService
from taifex_ingestor.services.ingestion_service import IngestionService


def main() -> None:
    """Run ingestion with default configuration."""
    configure_logging()
    config = AppConfig.from_env()

    http_client = HttpClient(
        timeout_seconds=config.timeout_seconds,
        user_agent=config.user_agent,
    )
    download_service = DownloadService(http_client=http_client)
    parser = TaifexParser()

    uploader = GcsUploader(config.gcs_bucket) if config.gcs_bucket else None
    service = IngestionService(
        config=config,
        download_service=download_service,
        parser=parser,
        uploader=uploader,
    )
    service.run()


if __name__ == "__main__":
    main()
