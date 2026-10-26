"""Entry point: download the shows, summarize them and save the report.

This file only wires the package together. It configures logging, and
its only print is the final line the user reads.
"""

import logging
import sys

from tvsummary import (
    DEFAULT_CONFIG_PATH,
    ResponseShapeError,
    TVMazeSource,
    TvSummaryError,
    build_run_info,
    build_summary,
    default_aggregations,
    load_settings,
    write_json,
)
from tvsummary.logging_setup import configure_logging

logger = logging.getLogger("tvsummary.main")


def main() -> None:
    """Download, summarize and save the shows, exiting cleanly on failure."""
    configure_logging("INFO")
    try:
        settings = load_settings(DEFAULT_CONFIG_PATH)
        configure_logging(settings.log_level)
        source = TVMazeSource(settings.source_url, settings.timeout_seconds)
        result = source.fetch()
        if not result.shows:
            raise ResponseShapeError("the download contained no usable show records.")
        summary = build_summary(
            result, default_aggregations(settings), settings.source_url
        )
        write_json(summary, settings.summary_path)
        write_json(
            build_run_info(settings, DEFAULT_CONFIG_PATH), settings.run_info_path
        )
    except TvSummaryError as error:
        logger.error("Run stopped: %s", error)
        sys.exit(f"Error: {error}")

    print(
        f"Processed {len(result.shows)} shows ({result.records_skipped} skipped). "
        f"Summary written to {settings.summary_path}."
    )


if __name__ == "__main__":
    main()
