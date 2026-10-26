"""Entry point: python -m tvsummary.main [--config PATH].

main() wires the package together. It is the only place that catches the
package's errors and the only place that prints: one success line to
standard output, or one line starting with "Error:" to standard error.
"""

import argparse
import logging
import sys
from pathlib import Path

from .aggregations import default_aggregations
from .config import DEFAULT_CONFIG_PATH, load_settings
from .errors import ResponseShapeError, TvSummaryError
from .logging_setup import configure_logging
from .report import build_run_info, build_summary, write_json
from .sources import TVMazeSource

logger = logging.getLogger(__name__)

EXIT_OK = 0
EXIT_FAILED = 1


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    """Read the command-line options."""
    parser = argparse.ArgumentParser(
        prog="python -m tvsummary.main",
        description="Summarize TV shows from the TVmaze API into a JSON report.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help=f"settings file to use (default: {DEFAULT_CONFIG_PATH.as_posix()})",
    )
    return parser.parse_args(argv)


def run(config_path: Path) -> str:
    """Do one full run and return the message to show the user.

    Raises a TvSummaryError subclass for any failure the program expects.
    """
    settings = load_settings(config_path)
    configure_logging(settings.log_level)
    logger.info("Using settings from %s", config_path)

    result = TVMazeSource(settings.source_url, settings.timeout_seconds).fetch()
    if not result.shows:
        raise ResponseShapeError("the download contained no usable show records.")

    summary = build_summary(result, default_aggregations(settings), settings.source_url)
    write_json(summary, settings.summary_path)
    write_json(build_run_info(settings, config_path), settings.run_info_path)
    logger.info("Run finished")
    return (
        f"Processed {len(result.shows)} shows ({result.records_skipped} skipped). "
        f"Summary written to {settings.summary_path.as_posix()}."
    )


def main(argv: list[str] | None = None) -> int:
    """Run the program and return the exit code: 0 on success, 1 on failure."""
    args = parse_args(argv)
    configure_logging("INFO")
    try:
        message = run(args.config)
    except TvSummaryError as error:
        logger.error("Run stopped: %s", error)
        print(f"Error: {error}", file=sys.stderr)
        return EXIT_FAILED
    print(message)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
