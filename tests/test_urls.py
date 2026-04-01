from txfno_data_bot.urls import resolve_link


def test_resolve_relative_link():
    base = "https://example.com/reports/index.html"
    assert resolve_link(base, "daily/fo_20260331.csv") == "https://example.com/reports/daily/fo_20260331.csv"


def test_resolve_absolute_link_kept_intact():
    base = "https://example.com/reports/index.html"
    absolute = "https://cdn.example.com/fo_20260331.csv"
    assert resolve_link(base, absolute) == absolute
