import io
from datetime import date
from zipfile import ZipFile

from taifex_ingestor.config import AppConfig
from taifex_ingestor.parsers.taifex_parser import TaifexParser
from taifex_ingestor.services.download_service import DownloadService
from taifex_ingestor.services.ingestion_service import IngestionService


class FakeHttpClientWithToday:
    def get_text(self, _url: str) -> str:
        return """
        <table>
          <tr><td>2026/04/01</td><td><a href='/downloads/sample_20260401.csv.zip'>csv</a></td></tr>
        </table>
        """

    def get_bytes(self, _url: str) -> bytes:
        buffer = io.BytesIO()
        with ZipFile(buffer, "w") as zf:
            zf.writestr("sample.csv", "a,b\n1,2\n")
        return buffer.getvalue()


class FakeHttpClientNoToday:
    def get_text(self, _url: str) -> str:
        return """
        <table>
          <tr><td>2026/03/31</td><td><a href='/downloads/sample_20260331.csv.zip'>csv</a></td></tr>
        </table>
        """

    def get_bytes(self, _url: str) -> bytes:
        raise AssertionError("should not download when target-date row is missing")


def _make_config(tmp_path):
    return AppConfig(
        output_dir=tmp_path,
        timeout_seconds=30,
        user_agent="agent",
        gcs_bucket=None,
        gcs_prefix="taifex/raw",
        futures_page_url="https://www.taifex.com.tw/cht/3/futPrevious30DaysSalesData",
        options_page_url="https://www.taifex.com.tw/cht/3/optPrevious30DaysSalesData",
        log_level="INFO",
    )


def test_ingestion_service_run_all_downloads_target_date(tmp_path):
    config = _make_config(tmp_path)
    http_client = FakeHttpClientWithToday()
    download_service = DownloadService(http_client=http_client, output_dir=tmp_path)

    service = IngestionService(
        config=config,
        http_client=http_client,
        parser=TaifexParser(),
        download_service=download_service,
        uploader=None,
    )

    results = service.run(target="all", target_date=date(2026, 4, 1))

    assert set(results.keys()) == {"futures", "options"}
    assert results["futures"].status == "downloaded"
    assert results["futures"].download is not None
    assert results["futures"].download.local_path.exists()


def test_ingestion_service_treats_no_target_file_as_non_error(tmp_path):
    config = _make_config(tmp_path)
    http_client = FakeHttpClientNoToday()
    download_service = DownloadService(http_client=http_client, output_dir=tmp_path)

    service = IngestionService(
        config=config,
        http_client=http_client,
        parser=TaifexParser(),
        download_service=download_service,
        uploader=None,
    )

    result = service.run(target="futures", target_date=date(2026, 4, 1))["futures"]

    assert result.status == "no_file_for_today"
    assert result.download is None
    assert result.upload is None
