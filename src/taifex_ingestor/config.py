"""Runtime configuration objects."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    """Application configuration for ingestion runs."""

    output_dir: Path = Path("data")
    timeout_seconds: int = 30
    user_agent: str = "taifex-ingestor/0.1.0"
    gcs_bucket: str | None = None

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create configuration using defaults for now."""
        return cls()
