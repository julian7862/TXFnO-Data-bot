from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re
from typing import Iterable

_DATE_PATTERNS = [
    re.compile(r"(20\d{2})[-_]?([01]\d)[-_]?([0-3]\d)"),
]


@dataclass(frozen=True)
class Candidate:
    url: str


def preferred_format(urls: Iterable[str]) -> str:
    """Prefer CSV when present, otherwise fall back to RPT.

    Returns one of: "csv", "rpt", or raises ValueError if neither exists.
    """
    lowered = [u.lower() for u in urls]
    if any(u.endswith(".csv") for u in lowered):
        return "csv"
    if any(u.endswith(".rpt") for u in lowered):
        return "rpt"
    raise ValueError("No CSV or RPT link found")


def extract_date(value: str) -> datetime:
    for pattern in _DATE_PATTERNS:
        match = pattern.search(value)
        if match:
            year, month, day = match.groups()
            return datetime(int(year), int(month), int(day))
    raise ValueError(f"Could not extract date from: {value}")


def latest_by_date(urls: Iterable[str]) -> str:
    items = list(urls)
    if not items:
        raise ValueError("No URLs provided")
    return max(items, key=extract_date)
