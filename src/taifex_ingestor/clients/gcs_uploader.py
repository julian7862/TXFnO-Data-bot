"""GCS upload client abstraction."""

from taifex_ingestor.exceptions import UploadError


class GcsUploader:
    """No-op uploader placeholder for future GCS integration."""

    def __init__(self, bucket_name: str) -> None:
        self.bucket_name = bucket_name

    def upload_text(self, object_name: str, data: str) -> None:
        if not self.bucket_name:
            raise UploadError("Bucket name is required for GCS uploads")
        # Placeholder: wire up google-cloud-storage in a later iteration.
        _ = (object_name, data)
