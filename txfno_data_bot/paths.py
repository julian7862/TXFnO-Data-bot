from __future__ import annotations

from datetime import date
from pathlib import Path
from urllib.parse import urlparse


def output_path(output_root: str | Path, trade_date: date, source_url: str) -> Path:
    root = Path(output_root)
    ext = Path(urlparse(source_url).path).suffix or ".dat"
    file_name = f"txfno_{trade_date.strftime('%Y%m%d')}{ext}"
    return root / str(trade_date.year) / f"{trade_date.month:02d}" / file_name
