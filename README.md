# TXFnO-Data-bot

## Ingestion services

This repository includes three composable services:

- `download_service.py`: downloads ZIP payloads, validates non-empty and ZIP structure, and stores files under `data/raw/{source}/{yyyy-mm-dd}/{filename}.zip`.
- `gcs_uploader.py`: uploads local ZIP files to `taifex/raw/{source}/{yyyy-mm-dd}/{filename}.zip` in GCS.
- `ingestion_service.py`: orchestrates `fetch -> parse -> download -> upload` for a single source or all registered sources.

### Idempotency strategy

This implementation uses **safe overwrite** for idempotency.

- Local files are written to deterministic paths, so reruns replace the same file.
- GCS uploads target deterministic object keys and overwrite the same object.
- Re-running ingestion for the same source/date produces a stable final state without duplicate objects.

### Logging and failures

The services log `source`, `date`, `url`, `local_path`, and `gcs_object` where applicable. They raise meaningful, stage-specific exceptions:

- `DownloadError`
- `UploadError`
- `IngestionError`
