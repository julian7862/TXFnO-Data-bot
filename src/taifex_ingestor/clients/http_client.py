"""HTTP client wrapper for downloading source payloads."""

from __future__ import annotations

import requests

from taifex_ingestor.exceptions import DownloadError


class HttpClient:
    """Thin requests wrapper with timeout/user-agent defaults."""

    def __init__(self, timeout_seconds: int, user_agent: str) -> None:
        self.timeout_seconds = timeout_seconds
        self.user_agent = user_agent

    def get(self, url: str) -> bytes:
        try:
            response = requests.get(
                url,
                timeout=self.timeout_seconds,
                headers={"User-Agent": self.user_agent},
            )
            response.raise_for_status()
            return response.content
        except requests.RequestException as exc:
            raise DownloadError(f"HTTP download failed for {url}") from exc
