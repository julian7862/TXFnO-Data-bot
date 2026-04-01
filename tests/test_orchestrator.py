from datetime import date

from txfno_data_bot.orchestrator import run_once


class MockHTTP:
    def __init__(self):
        self.bytes_calls = []

    def get_text(self, _url: str) -> str:
        return """
        <html><body>
          <a href=\"files/fo_20260330.rpt\">RPT 30</a>
          <a href=\"files/fo_20260330.csv\">CSV 30</a>
          <a href=\"files/fo_20260331.csv\">CSV 31</a>
        </body></html>
        """

    def get_bytes(self, url: str) -> bytes:
        self.bytes_calls.append(url)
        return b"sample-payload"


class MockUploader:
    def __init__(self):
        self.calls = []

    def upload_file(self, path):
        self.calls.append(path)
        return f"s3://bucket/{path.name}"


def test_run_once_orchestrates_download_write_and_upload(tmp_path):
    http = MockHTTP()
    uploader = MockUploader()

    result = run_once(
        index_url="https://example.com/reports/index.html",
        http_client=http,
        uploader=uploader,
        output_root=tmp_path,
        trade_date=date(2026, 3, 31),
    )

    assert result.source_url.endswith("fo_20260331.csv")
    assert result.destination.exists()
    assert result.destination.read_bytes() == b"sample-payload"
    assert http.bytes_calls == ["https://example.com/reports/files/fo_20260331.csv"]
    assert len(uploader.calls) == 1
    assert result.uploaded_to.startswith("s3://bucket/")
