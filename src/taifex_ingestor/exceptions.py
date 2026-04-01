"""Custom exception types for TAIFEX ingestion."""


class IngestionError(Exception):
    """Base class for ingestion failures."""


class DownloadError(IngestionError):
    """Raised when source download fails."""


class ParseError(IngestionError):
    """Raised when parsing a downloaded payload fails."""


class UploadError(IngestionError):
    """Raised when upload storage operation fails."""
