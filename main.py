"""Entry point: download the shows, summarize them and save the report.

This file only wires the package together and prints messages. All the
real work lives in src/tvsummary/.
"""

import sys

from tvsummary import (
    DownloadError,
    TVMazeSource,
    build_summary,
    default_aggregations,
    write_summary,
)
from tvsummary.config import OUTPUT_PATH, SOURCE_URL, TIMEOUT_SECONDS


def main():
    """Download, summarize and save the shows, exiting cleanly on failure."""
    print(f"Downloading shows from {SOURCE_URL} ...")
    source = TVMazeSource(SOURCE_URL, TIMEOUT_SECONDS)
    try:
        result = source.fetch()
    except DownloadError as err:
        sys.exit(f"Download failed: {err}")

    if not result.shows:
        sys.exit("Download succeeded but contained no usable show records.")

    summary = build_summary(result, default_aggregations(), SOURCE_URL)
    try:
        write_summary(summary, OUTPUT_PATH)
    except OSError as err:
        sys.exit(f"Could not write {OUTPUT_PATH}: {err.strerror}")

    print(
        f"Processed {len(result.shows)} shows ({result.records_skipped} skipped). "
        f"Summary written to {OUTPUT_PATH}."
    )


if __name__ == "__main__":
    main()
