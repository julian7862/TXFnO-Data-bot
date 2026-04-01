"""HTTP client wrapper for crawling pages and downloading artifacts."""

from __future__ import annotations

import requests

from taifex_ingestor.exceptions import DownloadError


class HttpClient:
    """Thin requests wrapper with timeout/user-agent defaults."""

    def __init__(self, timeout_seconds: int, user_agent: str) -> None:
        self.timeout_seconds = timeout_seconds
        self.user_agent = user_agent

    def _request(self, url: str) -> requests.Response:
        try:
            response = requests.get(
                url,
                timeout=self.timeout_seconds,
                headers={"User-Agent": self.user_agent},
            )
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            raise DownloadError(f"HTTP request failed for {url}") from exc

    def get_text(self, url: str) -> str:
        response = self._request(url)
        return response.text

    def get_bytes(self, url: str) -> bytes:
        response = self._request(url)
        return response.content
