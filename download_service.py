from __future__ import annotations

import io
import logging
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from zipfile import BadZipFile, ZipFile

import requests

LOGGER = logging.getLogger(__name__)


class DownloadError(RuntimeError):
    """Raised when downloading or persisting a ZIP fails."""


@dataclass(frozen=True)
class DownloadResult:
    source: str
    trade_date: date
    url: str
    local_path: Path


class DownloadService:
    """Download ZIP files into `data/raw/{source}/{yyyy-mm-dd}/{filename}.zip`."""

    def __init__(
        self,
        *,
        base_dir: str | Path = "data/raw",
        timeout_seconds: int = 30,
        session: requests.Session | None = None,
    ) -> None:
        self.base_dir = Path(base_dir)
        self.timeout_seconds = timeout_seconds
        self.session = session or requests.Session()

    def download_zip(
        self,
        *,
        source: str,
        trade_date: date,
        url: str,
        filename: str,
    ) -> DownloadResult:
        """Download a ZIP, validate that it is non-empty, and persist it locally."""
        destination = self.base_dir / source / trade_date.isoformat() / f"{filename}.zip"

        try:
            response = self.session.get(url, timeout=self.timeout_seconds)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise DownloadError(f"Failed to download ZIP from {url}: {exc}") from exc

        payload = response.content
        if not payload:
            raise DownloadError(f"Downloaded payload is empty for {url}")

        # Validate ZIP structure before writing to disk.
        try:
            with ZipFile(io.BytesIO(payload), "r") as zip_handle:
                if not zip_handle.namelist():
                    raise DownloadError(f"ZIP contains no entries for {url}")
        except BadZipFile as exc:
            raise DownloadError(f"Downloaded file is not a valid ZIP: {url}") from exc

        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload)

        LOGGER.info(
            "downloaded_zip",
            extra={
                "source": source,
                "date": trade_date.isoformat(),
                "url": url,
                "local_path": str(destination),
            },
        )

        return DownloadResult(source=source, trade_date=trade_date, url=url, local_path=destination)
