"""Parser for TAIFEX listing page rows and CSV ZIP links."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
import re

from taifex_ingestor.exceptions import ParseError
from taifex_ingestor.models import CrawlResult, SourceDefinition

_DATE_RE = re.compile(r"^\d{4}/\d{2}/\d{2}$")


@dataclass(frozen=True)
class _Candidate:
    row_index: int
    trading_date: date
    csv_zip_url: str


class _TableRowCollector(HTMLParser):
    """Collect table row cell text and row-level hrefs."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[tuple[list[str], list[str]]] = []
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
            self._current_text = []
            self._in_td = False
        elif tag == "tr" and self._in_tr:
            self.rows.append((self._current_cells, self._current_hrefs))
            self._in_tr = False


def _is_csv_zip_link(href: str) -> bool:
    path = urlparse(href).path.lower()
    return path.endswith(".csv.zip") and not path.endswith(".rpt.zip")


class TaifexParser:
    """Parse TAIFEX page HTML and resolve CSV ZIP link for a target date."""

    def find_for_date(self, source: SourceDefinition, html: str, target_date: date) -> CrawlResult | None:
        collector = _TableRowCollector()
        collector.feed(html)

        rows = [row for row in collector.rows if row[0]]
        if not rows:
            raise ParseError(f"No rows with cells found on page {source.page_url}")

        saw_valid_date = False
        candidates_for_day: list[_Candidate] = []
        for index, (cells, hrefs) in enumerate(rows):
            date_text = next((cell for cell in cells if _DATE_RE.fullmatch(cell)), None)
            if not date_text:
                continue

            try:
                trading_date = datetime.strptime(date_text, "%Y/%m/%d").date()
            except ValueError:
                continue

            saw_valid_date = True
            if trading_date != target_date:
                continue

            csv_links = [href for href in hrefs if _is_csv_zip_link(href)]
            if not csv_links:
                continue

            candidates_for_day.append(
                _Candidate(
                    row_index=index,
                    trading_date=trading_date,
                    csv_zip_url=urljoin(source.page_url, csv_links[0]),
                )
            )

        if not saw_valid_date:
            raise ParseError(
                f"No valid YYYY/MM/DD rows found on page {source.page_url}; page structure may have changed."
            )

        if not candidates_for_day:
            return None

        picked = max(candidates_for_day, key=lambda c: c.row_index)
        return CrawlResult(
            source=source,
            trading_date=picked.trading_date,
            csv_zip_url=picked.csv_zip_url,
        )
