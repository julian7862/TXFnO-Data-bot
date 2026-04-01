# TAIFEX Ingestor

A Python ingestion system for **two TAIFEX sources in one repository**:
- Futures source page: `https://www.taifex.com.tw/cht/3/futPrevious30DaysSalesData`
- Options source page: `https://www.taifex.com.tw/cht/3/optPrevious30DaysSalesData`

## Runtime behavior

For each source page, the runner:
1. Fetches page HTML.
2. Searches for the row matching the target date (default: today).
3. Extracts `.csv.zip` link only from that date row (ignores `.rpt.zip`).
4. If target-date CSV is missing, logs info and treats it as a normal non-trading-day / not-yet-published outcome.
5. If found, downloads and validates ZIP, then writes deterministic local path.
6. Uploads to GCS when bucket config is provided.

## CLI

```bash
python -m taifex_ingestor.cli run futures
python -m taifex_ingestor.cli run options
python -m taifex_ingestor.cli run all
# optional override date
python -m taifex_ingestor.cli run all --date 2026-04-01
```

Exit code:
- `0`: success (including no-file-for-target-date normal case)
- `1`: actual failure (network/parser/page-structure/download/upload)

## Environment variables

- `TAIFEX_FUTURES_PAGE_URL` (default: `https://www.taifex.com.tw/cht/3/futPrevious30DaysSalesData`)
- `TAIFEX_OPTIONS_PAGE_URL` (default: `https://www.taifex.com.tw/cht/3/optPrevious30DaysSalesData`)
- `TAIFEX_OUTPUT_DIR` (default: `data/raw`)
- `TAIFEX_TIMEOUT_SECONDS` (default: `30`)
- `TAIFEX_USER_AGENT` (default: `taifex-ingestor/0.1.0`)
- `TAIFEX_LOG_LEVEL` (default: `INFO`)
- `GCS_BUCKET_NAME` or `TAIFEX_GCS_BUCKET` (optional)
- `TAIFEX_GCS_PREFIX` (default: `taifex/raw`)

## GitHub Actions

Workflow: `.github/workflows/taifex_ingestion.yml`
- Daily schedule + manual dispatch
- Installs package dependencies
- Authenticates with GCP via GitHub secret
- Runs both sources: `python -m taifex_ingestor.cli run all`

## Testing

```bash
pytest -q
```
