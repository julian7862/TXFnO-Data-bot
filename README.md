# TXFnO-Data-bot

## GitHub Actions: TAIFEX ingestion workflow

The workflow file `.github/workflows/taifex_ingestion.yml` runs daily and can also be triggered manually.

### Required repository secrets

Configure the following secrets in your GitHub repository (`Settings` → `Secrets and variables` → `Actions`):

- `GCP_PROJECT_ID`: Google Cloud project ID.
- `GCS_BUCKET_NAME`: Target Google Cloud Storage bucket name.
- `GCP_SERVICE_ACCOUNT_KEY_JSON`: Full JSON key payload for a service account with access to write ingestion outputs.

### Optional repository variables (runtime config)

- `TAIFEX_ENV` (default: `production`)
- `TAIFEX_LOG_LEVEL` (default: `INFO`)
- `TAIFEX_MAX_RETRIES` (default: `3`)
