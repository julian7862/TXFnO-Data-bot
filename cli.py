"""Command-line interface for TXFnO data bot runners."""

from __future__ import annotations

import argparse
import logging
from datetime import date

from logging_config import configure_logging

logger = logging.getLogger(__name__)


class RunnerError(RuntimeError):
    """Raised when a pipeline runner fails."""


def run_futures(run_date: date | None = None) -> None:
    """Run the futures pipeline."""

    logger.info("starting futures pipeline", extra={"pipeline": "futures", "run_date": run_date})
    # TODO: wire actual futures run flow.
    logger.info("completed futures pipeline", extra={"pipeline": "futures", "run_date": run_date})


def run_options(run_date: date | None = None) -> None:
    """Run the options pipeline."""

    logger.info("starting options pipeline", extra={"pipeline": "options", "run_date": run_date})
    # TODO: wire actual options run flow.
    logger.info("completed options pipeline", extra={"pipeline": "options", "run_date": run_date})


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TXFnO data bot CLI")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set logging verbosity.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="Run one or more pipelines")
    run_subparsers = run_parser.add_subparsers(dest="runner", required=True)

    for runner_name in ("futures", "options", "all"):
        subparser = run_subparsers.add_parser(runner_name, help=f"Run {runner_name} pipeline")
        subparser.add_argument(
            "--date",
            type=date.fromisoformat,
            required=False,
            help="Optional run date in YYYY-MM-DD format.",
        )

    return parser.parse_args()


def _run_selected_pipeline(runner: str, run_date: date | None) -> int:
    failures = []

    if runner in {"futures", "all"}:
        try:
            run_futures(run_date=run_date)
        except Exception as exc:  # noqa: BLE001 - propagate failure as exit code
            failures.append(("futures", exc))
            logger.exception("pipeline failed", extra={"pipeline": "futures", "run_date": run_date})

    if runner in {"options", "all"}:
        try:
            run_options(run_date=run_date)
        except Exception as exc:  # noqa: BLE001 - propagate failure as exit code
            failures.append(("options", exc))
            logger.exception("pipeline failed", extra={"pipeline": "options", "run_date": run_date})

    if failures:
        logger.error(
            "one or more pipelines failed",
            extra={"failed_pipelines": ",".join(name for name, _ in failures), "run_date": run_date},
        )
        return 1

    logger.info("all selected pipelines completed", extra={"runner": runner, "run_date": run_date})
    return 0


def main() -> int:
    args = _parse_args()
    configure_logging(args.log_level)

    if args.command != "run":
        logger.error("unknown command", extra={"command": args.command})
        return 1

    run_date = getattr(args, "date", None)
    return _run_selected_pipeline(args.runner, run_date)


if __name__ == "__main__":
    raise SystemExit(main())
