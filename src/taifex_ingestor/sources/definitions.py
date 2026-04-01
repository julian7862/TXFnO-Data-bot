"""Source definitions for TAIFEX market datasets.

The templates below keep shared definition fields in one place,
so futures/options only vary by source type and URL.
"""

from taifex_ingestor.enums import SourceType
from taifex_ingestor.models import SourceDefinition

_BASE_SOURCE = {
    "name": "taifex_daily_market_report",
}

SOURCE_DEFINITIONS: dict[SourceType, SourceDefinition] = {
    SourceType.FUTURES: SourceDefinition(
        **_BASE_SOURCE,
        source_type=SourceType.FUTURES,
        url="https://www.taifex.com.tw/file/taifex/Dailydownload/DailyFuture.zip",
    ),
    SourceType.OPTIONS: SourceDefinition(
        **_BASE_SOURCE,
        source_type=SourceType.OPTIONS,
        url="https://www.taifex.com.tw/file/taifex/Dailydownload/DailyOption.zip",
    ),
}
