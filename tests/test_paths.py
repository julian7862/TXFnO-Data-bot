from datetime import date

from txfno_data_bot.paths import output_path


def test_output_path_generates_partitioned_path_and_filename():
    path = output_path("/tmp/out", date(2026, 3, 31), "https://example.com/fo_20260331.csv")
    assert str(path) == "/tmp/out/2026/03/txfno_20260331.csv"


def test_output_path_uses_dat_extension_when_missing():
    path = output_path("/tmp/out", date(2026, 3, 31), "https://example.com/fo_20260331")
    assert path.name == "txfno_20260331.dat"
