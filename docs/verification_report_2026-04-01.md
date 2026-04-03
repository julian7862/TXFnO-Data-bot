# Strict Verification Review (2026-04-01)

## 1. Overall Status

**Status: Yellow (partially complete / notable gaps).**

The `src/taifex_ingestor` package implements most of the intended ingestion behavior (exact TAIFEX page defaults, target-date matching, CSV-only filtering, non-trading-day handling, deterministic download pathing, optional GCS upload, CLI orchestration). However, the repository also contains a legacy/parallel implementation (`txfno_data_bot/` + root-level modules + separate `cli.py`) that is architecturally inconsistent and includes behavior that violates critical business rules (e.g., selecting latest available data instead of target date). This duplicate code and test suite mixing creates operational and maintenance risk.

## 2. Verification Scorecard

| Area | Status | Evidence | Notes |
|---|---|---|---|
| Exact source pages | **Implemented (in primary package)** | `AppConfig` defaults futures/options URLs to the exact required pages. | URLs are configurable via env (good), but no guardrails prevent accidental override to wrong pages. |
| Target-date behavior | **Implemented (in primary package)** | `IngestionService.run` uses `date.today()` by default and passes explicit `target_date`; parser filters rows by `trading_date == target_date`. | No fallback to “latest row” in primary package. |
| CSV extraction | **Implemented (with parser-robustness caveat)** | Parser only accepts links whose path ends with `.csv.zip` and excludes `.rpt.zip`; uses `urljoin` for relative URLs. | If target-date row exists but only RPT exists, parser returns `None` (treated as no-file); this may mask data quality issues unless explicitly intended. |
| Non-trading-day handling | **Implemented** | If parser returns `None`, service logs info and returns status `no_file_for_today` instead of raising. CLI returns `0` unless an exception escapes. | Behavior aligns with business rule #4/#5 for normal no-file cases. |
| Repository structure | **Needs Refactor** | Clean layered structure exists under `src/taifex_ingestor/...`, but duplicate older flows also exist at repo root and `txfno_data_bot/`. | Mixed implementations reduce clarity of source-of-truth architecture. |
| Shared architecture for two crawlers | **Implemented (in primary package)** | Source-specific differences isolated via `SourceType` + `SourceDefinition` mapping; common services reused. | Legacy code does not represent the two-page architecture and should be retired. |
| Download flow | **Implemented (baseline)** | Download validates non-empty payload and ZIP integrity; writes deterministic path by source/date/filename. | No retry/backoff logic in active HTTP path. |
| GCS upload | **Implemented (baseline)** | Uses `google.cloud.storage.Client()` with env-based auth; no hardcoded credentials; deterministic object key. | Upload exception handling is broad in active package (`except Exception`). |
| CLI / run flow | **Implemented (primary CLI)** | Supports `run futures|options|all` and optional `--date`; exits `1` on exception, else `0`. | Root-level legacy `cli.py` has TODO stubs and is non-authoritative but still present. |
| GitHub Actions | **Partial** | Workflow has daily cron + manual dispatch, Python setup, install, GCP auth, run all sources. | Workflow assumes all no-file outcomes are non-errors (true today), but no explicit assertion/reporting of per-source status to distinguish no-file vs download in job output. |
| Config / env management | **Implemented (primary package)** | Centralized in `AppConfig.from_env` with key runtime knobs. | Workflow exports unused env `TAIFEX_MAX_RETRIES`; app has no retries config field. |
| Tests | **Partial / Needs Refactor** | Good tests for parser target-date and no-file flow in `taifex_ingestor`; all tests currently pass. | Test suite also includes legacy module tests that validate outdated “latest” behavior and non-TAIFEX logic, creating fake completeness. |
| Documentation | **Partial** | README documents intended behavior, CLI, env vars, workflow. | Does not clearly declare legacy modules as deprecated or unsupported. |
| Idempotency / operational safety | **Partial** | Deterministic local path and deterministic GCS object naming imply overwrite behavior. | Explicit idempotency policy is not documented in active package comments/tests; no duplicate-detection semantics beyond overwrite. |

## 3. Findings

### Correctly Implemented

1. **Exact intended TAIFEX source pages are configured by default** in active config.
2. **Target-date selection is explicit** and does not choose the latest row in active parser/service flow.
3. **CSV ZIP filtering is explicit** (`.csv.zip` accepted, `.rpt.zip` rejected).
4. **No-file-for-today is treated as normal** (informational log + non-error status).
5. **End-to-end flow is modular in active package**: config, HTTP client, parser, download service, uploader, orchestration, CLI.
6. **Daily GitHub Actions schedule and manual dispatch exist**, with GCP authentication step.

### Partially Implemented

1. **GitHub Actions operational observability** is weak: job logs do not summarize per-source outcome categories (downloaded vs no-file).
2. **Retries/timeouts**: timeout exists, retries not implemented in active HTTP client.
3. **Idempotency** is de facto overwrite-by-key but not clearly asserted by tests/docs for active package.
4. **Documentation completeness** is decent for new package but incomplete regarding removal/deprecation of old paths.

### Missing

1. **No explicit test asserting exact configured source URLs are unchanged** (e.g., guard test to prevent accidental drift to `dl*` pages).
2. **No integration-style test around workflow/CLI status mapping** for mixed outcomes (e.g., futures no-file + options success).
3. **No explicit parser-change sentinel tests** using realistic TAIFEX HTML snapshots (to catch table-structure drift).

### Incorrectly Implemented

1. **Legacy implementation violates critical business rule #2** (target-date behavior): `txfno_data_bot/orchestrator.py` picks `latest_by_date(...)` after choosing format, not row matching today.
2. **Legacy parser/tests emphasize latest-date URL extraction**, not strict TAIFEX row-date match behavior.
3. **Root-level alternate CLI has TODO runner stubs**, making repository appear complete while containing non-functional parallel entrypoints.

### Design / Code Quality Risks

1. **Dual architecture risk**: two overlapping codepaths (`src/taifex_ingestor` vs legacy modules) can cause wrong module import/use in automation.
2. **Fake completeness risk**: passing tests include both new and old systems; green CI does not guarantee the intended production architecture alone.
3. **Error taxonomy blur**: in active parser, “target-date row exists but only non-CSV links” collapses to `None` (same as non-trading day), which may hide source regression.
4. **Broad upload exception catch** may hide actionable GCS exception categories.

## 4. Exact Gaps to Fix Next

### 1) Critical

1. **Retire or isolate legacy code paths** (`txfno_data_bot/`, root-level ingestion/download/parser/cli modules) from production and CI execution.
2. **Add guard tests for exact source page URLs** to prevent regression to non-canonical endpoints (e.g., `dlFut...`, `dlOpt...`).
3. **Clarify no-file taxonomy**: distinguish “no row for target date” vs “row exists but CSV link missing” in status/logging.

### 2) Important

1. Add **retry/backoff** to HTTP client with bounded attempts and clear logging.
2. Add **integration tests** for CLI exit code behavior across mixed source outcomes and real failures.
3. Tighten **GCS exception handling** to capture known cloud exceptions distinctly.

### 3) Nice to have

1. Add TAIFEX HTML fixture snapshots and parser contract tests.
2. Emit structured summary in workflow logs/artifacts per source (`downloaded`, `no_file_for_today`, `failed`).
3. Document explicit idempotency behavior (overwrite semantics) in README.

## 5. Refactor Advice

1. **Single source of truth package**: make `src/taifex_ingestor` the only supported runtime path; remove or deprecate legacy modules and tests.
2. **Strengthen domain status model**: replace free-form `status: str` with an enum (e.g., `DOWNLOADED`, `NO_ROW_FOR_DATE`, `ROW_WITHOUT_CSV`, `FAILED`) for observability and policy control.
3. **Enforce config invariants**: optional strict mode that rejects non-canonical source URLs in production.
4. **Testing pyramid cleanup**: separate unit tests for parser/service from compatibility tests; avoid validating deprecated behavior in default CI.

## 6. Final Verdict

**Needs targeted fixes before merge.**

Primary implementation quality is close, but repository-level architecture is not cleanly production-ready due to duplicate/contradictory code paths and insufficient guardrails against critical rule regressions.
