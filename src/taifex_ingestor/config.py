"""Runtime configuration objects."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    """Application configuration for ingestion runs."""

    output_dir: Path
    timeout_seconds: int
    user_agent: str
    gcs_bucket: str | None
    gcs_prefix: str
    futures_page_url: str
    options_page_url: str
    log_level: str

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create configuration from environment variables."""
        return cls(
            output_dir=Path(os.getenv("TAIFEX_OUTPUT_DIR", "data/raw")),
            timeout_seconds=int(os.getenv("TAIFEX_TIMEOUT_SECONDS", "30")),
            user_agent=os.getenv("TAIFEX_USER_AGENT", "taifex-ingestor/0.1.0"),
            gcs_bucket=os.getenv("GCS_BUCKET_NAME") or os.getenv("TAIFEX_GCS_BUCKET") or None,
            gcs_prefix=os.getenv("TAIFEX_GCS_PREFIX", "taifex/raw"),
            futures_page_url=os.getenv(
                "TAIFEX_FUTURES_PAGE_URL",
                "https://www.taifex.com.tw/cht/3/futPrevious30DaysSalesData",
            ),
            options_page_url=os.getenv(
                "TAIFEX_OPTIONS_PAGE_URL",
                "https://www.taifex.com.tw/cht/3/optPrevious30DaysSalesData",
            ),
            log_level=os.getenv("TAIFEX_LOG_LEVEL", "INFO").upper(),
        )
