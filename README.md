# TXFnO-Data-bot

TXFnO-Data-bot downloads the latest FnO report file from a listing page, writes it deterministically to disk, and uploads it through a pluggable uploader interface.

## Architecture summary

The project is intentionally small and split into focused modules:

- `txfno_data_bot.parser`
  - Chooses preferred source format (`.csv` preferred over `.rpt`).
  - Extracts embedded dates from candidate links and selects the latest available report.
- `txfno_data_bot.urls`
  - Resolves relative links against the index URL and preserves absolute links.
- `txfno_data_bot.paths`
  - Builds deterministic, date-partitioned output paths and canonical filenames.
- `txfno_data_bot.orchestrator`
  - Coordinates scraping links, choosing the best source file, downloading bytes, writing locally, and calling uploader.

## Repository tree

```text
.
├── .env.example
├── README.md
├── tests
│   ├── test_orchestrator.py
│   ├── test_parser.py
│   ├── test_paths.py
│   └── test_urls.py
└── txfno_data_bot
    ├── __init__.py
    ├── orchestrator.py
    ├── parser.py
    ├── paths.py
    └── urls.py
```

## Local setup and CLI usage

### 1) Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip pytest
```

### 2) Configure environment

```bash
cp .env.example .env
# edit .env for your environment
```

### 3) Run tests

```bash
pytest -q
```

### 4) Example orchestration usage (Python entrypoint)

```python
from datetime import date
from txfno_data_bot.orchestrator import run_once

# Provide concrete implementations in production.
result = run_once(
    index_url="https://example.com/reports/index.html",
    http_client=my_http_client,
    uploader=my_uploader,
    output_root="./data",
    trade_date=date.today(),
)
print(result)
```

## Idempotency behavior

- The bot always resolves to a single latest source URL per run.
- Local output path is deterministic by trade date (`YYYY/MM/txfno_YYYYMMDD.ext`).
- Re-running the same date/source overwrites the same local file path (no duplicate filenames).
- Upload idempotency depends on uploader implementation:
  - object-store uploaders should use deterministic object keys
  - upsert/overwrite behavior should be enabled on destination

## GitHub Actions setup and secrets

Create a workflow that:
1. checks out the repo,
2. sets up Python,
3. installs dependencies,
4. runs `pytest`.

Recommended repository secrets/variables (only if required by your uploader/runtime):

- `TXFNO_INDEX_URL` (can also be a plain Actions variable)
- `TXFNO_UPLOAD_BUCKET`
- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_REGION` (if using S3)
- any provider-specific token required by your uploader backend

Never commit `.env` with real credentials.

## Troubleshooting and expected logs

### Expected log flow (INFO level)

- "Fetched index page"
- "Discovered N candidate links"
- "Selected format: csv|rpt"
- "Selected latest source: <url>"
- "Wrote local file: <path>"
- "Uploaded artifact: <destination>"

### Common issues

- **No CSV or RPT link found**
  - The source page HTML changed or links are generated dynamically.
- **Could not extract date from URL**
  - Filename/date format in source links is unsupported.
- **Upload failure**
  - Missing credentials, bucket misconfiguration, or network/ACL issues.
- **Unexpected file extension**
  - Source link has no extension; bot defaults to `.dat`.

## Runtime environment variables

See `.env.example` for the canonical list and defaults.
