from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError

LOGGER = logging.getLogger(__name__)


class UploadError(RuntimeError):
    """Raised when uploading raw artifacts to GCS fails."""


@dataclass(frozen=True)
class UploadResult:
    source: str
    trade_date: date
    local_path: Path
    gcs_object: str


class GCSUploader:
    """Upload local files to `taifex/raw/{source}/{yyyy-mm-dd}/{filename}.zip`.

    Idempotency strategy: safe overwrite.
    Uploading the same local file path and object key multiple times is intentional and
    deterministic; the latest bytes replace the existing object content.
    """

    def __init__(
        self,
        *,
        bucket_name: str,
        prefix: str = "taifex/raw",
        client: storage.Client | None = None,
    ) -> None:
        self.bucket_name = bucket_name
        self.prefix = prefix.strip("/")
        self.client = client or storage.Client()

    def upload_zip(
        self,
        *,
        source: str,
        trade_date: date,
        filename: str,
        local_path: str | Path,
    ) -> UploadResult:
        local = Path(local_path)
        if not local.exists():
            raise UploadError(f"Cannot upload missing file: {local}")

        object_name = f"{self.prefix}/{source}/{trade_date.isoformat()}/{filename}.zip"
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(object_name)

        try:
            blob.upload_from_filename(str(local))
        except GoogleCloudError as exc:
            raise UploadError(
                f"Failed to upload {local} to gs://{self.bucket_name}/{object_name}: {exc}"
            ) from exc

        LOGGER.info(
            "uploaded_zip",
            extra={
                "source": source,
                "date": trade_date.isoformat(),
                "local_path": str(local),
                "gcs_object": f"gs://{self.bucket_name}/{object_name}",
            },
        )

        return UploadResult(
            source=source,
            trade_date=trade_date,
            local_path=local,
            gcs_object=object_name,
        )
