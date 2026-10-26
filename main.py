"""Entry point: download the shows, summarize them and save the report.

This file only wires the package together and prints messages. All the
real work lives in src/tvsummary/.
"""

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


def main():
    """Download, summarize and save the shows, exiting cleanly on failure."""
    print(f"Downloading shows from {SOURCE_URL} ...")
    try:
        result = TVMazeSource(SOURCE_URL, TIMEOUT_SECONDS).fetch()
        if not result.shows:
            raise ResponseShapeError("the download contained no usable show records.")
        summary = build_summary(result, default_aggregations(), SOURCE_URL)
        write_summary(summary, OUTPUT_PATH)
    except TvSummaryError as error:
        sys.exit(f"Error: {error}")

    print(
        f"Processed {len(result.shows)} shows ({result.records_skipped} skipped). "
        f"Summary written to {OUTPUT_PATH}."
    )


if __name__ == "__main__":
    main()
