from datetime import date

from taifex_ingestor.enums import SourceType
from taifex_ingestor.models import SourceDefinition
from taifex_ingestor.parsers.taifex_parser import TaifexParser


def test_parser_finds_target_date_csv_zip_and_ignores_rpt_zip() -> None:
    html = """
    <table>
      <tr><td>2026/04/01</td><td><a href='/DailyDownload/Daily_20260401.rpt.zip'>rpt</a></td></tr>
      <tr><td>2026/04/01</td><td><a href='/DailyDownload/Daily_20260401.csv.zip'>csv</a></td></tr>
      <tr><td>2026/03/31</td><td><a href='/DailyDownload/Daily_20260331.csv.zip'>old</a></td></tr>
    </table>
    """
    source = SourceDefinition(
        name="futures",
        source_type=SourceType.FUTURES,
        page_url="https://www.taifex.com.tw/cht/3/futPrevious30DaysSalesData",
    )

    result = TaifexParser().find_for_date(source, html, target_date=date(2026, 4, 1))

    assert result is not None
    assert result.trading_date.isoformat() == "2026-04-01"
    assert result.csv_zip_url.endswith("Daily_20260401.csv.zip")


def test_parser_returns_none_when_target_date_not_found() -> None:
    html = """
    <table>
      <tr><td>2026/03/31</td><td><a href='/DailyDownload/Daily_20260331.csv.zip'>old</a></td></tr>
    </table>
    """
    source = SourceDefinition(
        name="options",
        source_type=SourceType.OPTIONS,
        page_url="https://www.taifex.com.tw/cht/3/optPrevious30DaysSalesData",
    )

    result = TaifexParser().find_for_date(source, html, target_date=date(2026, 4, 1))

    assert result is None
