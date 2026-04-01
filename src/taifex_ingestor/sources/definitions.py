"""Source definitions for TAIFEX market datasets."""

from __future__ import annotations

from taifex_ingestor.config import AppConfig
from taifex_ingestor.enums import SourceType
from taifex_ingestor.models import SourceDefinition


def build_source_definitions(config: AppConfig) -> dict[SourceType, SourceDefinition]:
    """Build source definitions from runtime config."""
    return {
        SourceType.FUTURES: SourceDefinition(
            name="taifex_futures_daily",
            source_type=SourceType.FUTURES,
            page_url=config.futures_page_url,
        ),
        SourceType.OPTIONS: SourceDefinition(
            name="taifex_options_daily",
            source_type=SourceType.OPTIONS,
            page_url=config.options_page_url,
        ),
    }
