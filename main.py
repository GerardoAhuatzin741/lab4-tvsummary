"""Entry point: download the shows, summarize them and save the report.

This file only wires the package together. It configures logging, and
its only print is the final line the user reads.
"""

import logging
import sys

from tvsummary import (
    ResponseShapeError,
    TVMazeSource,
    TvSummaryError,
    build_summary,
    default_aggregations,
    write_summary,
)
from tvsummary.config import OUTPUT_PATH, SOURCE_URL, TIMEOUT_SECONDS
from tvsummary.logging_setup import configure_logging

logger = logging.getLogger("tvsummary.main")


def main():
    """Download, summarize and save the shows, exiting cleanly on failure."""
    configure_logging("INFO")
    try:
        result = TVMazeSource(SOURCE_URL, TIMEOUT_SECONDS).fetch()
        if not result.shows:
            raise ResponseShapeError("the download contained no usable show records.")
        summary = build_summary(result, default_aggregations(), SOURCE_URL)
        write_summary(summary, OUTPUT_PATH)
    except TvSummaryError as error:
        logger.error("Run stopped: %s", error)
        sys.exit(f"Error: {error}")

    print(
        f"Processed {len(result.shows)} shows ({result.records_skipped} skipped). "
        f"Summary written to {OUTPUT_PATH}."
    )


if __name__ == "__main__":
    main()
