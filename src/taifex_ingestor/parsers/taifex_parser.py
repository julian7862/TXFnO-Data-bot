"""Parser for TAIFEX CSV-like payloads."""

from __future__ import annotations

import csv
from io import StringIO

from taifex_ingestor.exceptions import ParseError
from taifex_ingestor.models import ParsedRecord, SourceDefinition


class TaifexParser:
    """Parse TAIFEX text payload into records."""

    def parse(self, source: SourceDefinition, content: bytes) -> list[ParsedRecord]:
        try:
            text = content.decode("utf-8-sig")
            reader = csv.DictReader(StringIO(text))
            return [ParsedRecord(source_name=source.name, row=dict(row)) for row in reader]
        except Exception as exc:  # noqa: BLE001
            raise ParseError(f"Failed to parse payload for {source.source_type}") from exc
