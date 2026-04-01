from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re

from .parser import latest_by_date, preferred_format
from .paths import output_path
from .urls import resolve_link


_HREF_RE = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)


@dataclass
class RunResult:
    source_url: str
    destination: Path
    uploaded_to: str


def _extract_links(html: str) -> list[str]:
    return _HREF_RE.findall(html)


def run_once(index_url: str, http_client, uploader, output_root: str | Path, trade_date: date) -> RunResult:
    index_html = http_client.get_text(index_url)
    links = [resolve_link(index_url, href) for href in _extract_links(index_html)]

    picked_format = preferred_format(links)
    format_links = [u for u in links if u.lower().endswith(f".{picked_format}")]
    source_url = latest_by_date(format_links)

    payload = http_client.get_bytes(source_url)
    destination = output_path(output_root, trade_date, source_url)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)

    uploaded_to = uploader.upload_file(destination)
    return RunResult(source_url=source_url, destination=destination, uploaded_to=uploaded_to)
