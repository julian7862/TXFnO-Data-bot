import pytest

from txfno_data_bot.parser import latest_by_date, preferred_format


def test_preferred_format_selects_csv_over_rpt():
    links = [
        "https://example.com/fo_20260330.rpt",
        "https://example.com/fo_20260330.csv",
    ]
    assert preferred_format(links) == "csv"


def test_preferred_format_falls_back_to_rpt():
    links = ["https://example.com/fo_20260330.rpt"]
    assert preferred_format(links) == "rpt"


def test_latest_by_date_picks_newest_embedded_date():
    links = [
        "https://example.com/fo_2026-03-29.csv",
        "https://example.com/fo_20260331.csv",
        "https://example.com/fo_20260330.csv",
    ]
    assert latest_by_date(links).endswith("20260331.csv")


def test_latest_by_date_errors_when_no_dates_found():
    with pytest.raises(ValueError):
        latest_by_date(["https://example.com/fo_latest.csv"])
