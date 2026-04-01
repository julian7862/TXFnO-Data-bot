from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
import re

from models import TaifexCrawlResult, TaifexRowCandidate


_DATE_RE = re.compile(r"^\d{4}/\d{2}/\d{2}$")


class TaifexParserError(Exception):
    """Base error for TAIFEX parsing issues."""


class TableStructureError(TaifexParserError):
    """Raised when TAIFEX HTML no longer follows expected row/cell structure."""


class NoValidCsvLinkError(TaifexParserError):
    """Raised when no row contains a valid .csv.zip link."""


@dataclass(slots=True)
class _RawRow:
    cells: list[str]
    hrefs: list[str]


class _TableRowCollector(HTMLParser):
    """Collect all TR/TD text and anchor href values from a TAIFEX page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[_RawRow] = []

        self._in_tr = False
        self._in_td = False
        self._current_text: list[str] = []
        self._current_cells: list[str] = []
        self._current_hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tr":
            self._in_tr = True
            self._current_cells = []
            self._current_hrefs = []
        elif self._in_tr and tag == "td":
            self._in_td = True
            self._current_text = []
        elif self._in_tr and tag == "a":
            href = dict(attrs).get("href")
            if href:
                self._current_hrefs.append(href.strip())

    def handle_data(self, data: str) -> None:
        if self._in_tr and self._in_td:
            self._current_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "td" and self._in_td:
            text = " ".join(chunk.strip() for chunk in self._current_text if chunk.strip()).strip()
            self._current_cells.append(text)
            self._in_td = False
            self._current_text = []
        elif tag == "tr" and self._in_tr:
            self.rows.append(_RawRow(cells=self._current_cells, hrefs=self._current_hrefs))
            self._in_tr = False


def _parse_strict_date(value: str):
    if not _DATE_RE.fullmatch(value):
        return None
    try:
        return datetime.strptime(value, "%Y/%m/%d").date()
    except ValueError:
        return None


def _is_csv_zip_link(href: str) -> bool:
    path = urlparse(href).path.lower()
    return path.endswith(".csv.zip") and not path.endswith(".rpt.zip")


def parse_table_rows(html: str, page_url: str) -> list[TaifexRowCandidate]:
    """Parse TAIFEX HTML and return rows with strict dates and valid CSV ZIP links."""
    collector = _TableRowCollector()
    collector.feed(html)

    rows_with_cells = [row for row in collector.rows if row.cells]
    if not rows_with_cells:
        raise TableStructureError("No table rows with cells found in TAIFEX page HTML.")

    candidates: list[TaifexRowCandidate] = []
    rows_with_date = 0

    for index, row in enumerate(rows_with_cells):
        date_text = next((cell for cell in row.cells if _DATE_RE.fullmatch(cell)), None)
        if not date_text:
            continue

        trading_date = _parse_strict_date(date_text)
        if trading_date is None:
            continue

        rows_with_date += 1

        csv_hrefs = [href for href in row.hrefs if _is_csv_zip_link(href)]
        if not csv_hrefs:
            continue

        resolved_url = urljoin(page_url, csv_hrefs[0])
        candidates.append(
            TaifexRowCandidate(
                row_index=index,
                trading_date=trading_date,
                date_text=date_text,
                csv_zip_url=resolved_url,
            )
        )

    if rows_with_date == 0:
        raise TableStructureError("No strict YYYY/MM/DD date column was found in TAIFEX rows.")

    if not candidates:
        raise NoValidCsvLinkError(
            "No valid CSV ZIP link found. Expected links ending with .csv.zip and not .rpt.zip."
        )

    return candidates


def select_latest_row(candidates: list[TaifexRowCandidate]) -> TaifexRowCandidate:
    """Return the latest row by trading date."""
    if not candidates:
        raise NoValidCsvLinkError("Cannot select latest row from an empty candidate list.")
    return max(candidates, key=lambda row: (row.trading_date, row.row_index))


def parse_latest_crawl_result(html: str, page_url: str) -> TaifexCrawlResult:
    """Parse TAIFEX page HTML and return the latest downloadable CSV row."""
    collector = _TableRowCollector()
    collector.feed(html)
    total_rows_seen = len([r for r in collector.rows if r.cells])

    candidates = parse_table_rows(html=html, page_url=page_url)
    latest = select_latest_row(candidates)

    return TaifexCrawlResult(
        page_url=page_url,
        latest=latest,
        total_rows_seen=total_rows_seen,
        total_candidates=len(candidates),
    )
