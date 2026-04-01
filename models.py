from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class TaifexRowCandidate:
    """A TAIFEX table row that contains a valid date and CSV ZIP link."""

    row_index: int
    trading_date: date
    date_text: str
    csv_zip_url: str


@dataclass(frozen=True, slots=True)
class TaifexCrawlResult:
    """Final parser output containing the latest available downloadable row."""

    page_url: str
    latest: TaifexRowCandidate
    total_rows_seen: int
    total_candidates: int
