"""GCS upload client abstraction."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from taifex_ingestor.exceptions import UploadError
from taifex_ingestor.models import DownloadResult, UploadResult


class GcsUploader:
    """Upload ZIP files to GCS with deterministic object naming."""

    def __init__(self, bucket_name: str, prefix: str = "taifex/raw", client: Any | None = None) -> None:
        self.bucket_name = bucket_name
        self.prefix = prefix.strip("/")
        if client is not None:
            self.client = client
        else:
            from google.cloud import storage

            self.client = storage.Client()

    def _object_name(self, download: DownloadResult) -> str:
        filename = Path(download.local_path).name
        return (
            f"{self.prefix}/{download.source.source_type.value}/"
            f"{download.trading_date.isoformat()}/{filename}"
        )

    def upload_file(self, download: DownloadResult) -> UploadResult:
        local = Path(download.local_path)
        if not local.exists():
            raise UploadError(f"Cannot upload missing file: {local}")

        object_name = self._object_name(download)
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(object_name)

        try:
            blob.upload_from_filename(str(local))
        except Exception as exc:  # noqa: BLE001
            raise UploadError(
                f"Failed to upload {local} to gs://{self.bucket_name}/{object_name}"
            ) from exc

        return UploadResult(
            source=download.source,
            trading_date=download.trading_date,
            object_name=object_name,
        )
