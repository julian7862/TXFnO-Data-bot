"""CLI entrypoint for TAIFEX ingestor."""

from __future__ import annotations

import argparse
import logging
from datetime import date

from taifex_ingestor.clients.gcs_uploader import GcsUploader
from taifex_ingestor.clients.http_client import HttpClient
from taifex_ingestor.config import AppConfig
from taifex_ingestor.logging_config import configure_logging
from taifex_ingestor.parsers.taifex_parser import TaifexParser
from taifex_ingestor.services.download_service import DownloadService
from taifex_ingestor.services.ingestion_service import IngestionService


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TAIFEX ingestion CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run ingestion")
    run_parser.add_argument("target", choices=["futures", "options", "all"])
    run_parser.add_argument("--date", type=date.fromisoformat, required=False)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    config = AppConfig.from_env()
    configure_logging(getattr(logging, config.log_level, logging.INFO))

    http_client = HttpClient(
        timeout_seconds=config.timeout_seconds,
        user_agent=config.user_agent,
    )
    parser = TaifexParser()
    download_service = DownloadService(http_client=http_client, output_dir=config.output_dir)
    uploader = GcsUploader(config.gcs_bucket, prefix=config.gcs_prefix) if config.gcs_bucket else None

    service = IngestionService(
        config=config,
        http_client=http_client,
        parser=parser,
        download_service=download_service,
        uploader=uploader,
    )

    try:
        service.run(target=args.target, target_date=args.date)
    except Exception:
        logging.getLogger(__name__).exception("ingestion failed")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
