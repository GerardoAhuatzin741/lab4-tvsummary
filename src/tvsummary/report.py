"""Building the summary dict and writing it to disk."""

import json
import logging
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .aggregations import Aggregation
from .errors import OutputError
from .sources import FetchResult

logger = logging.getLogger(__name__)


def build_summary(
    result: FetchResult, aggregations: Sequence[Aggregation], source_url: str
) -> dict[str, Any]:
    """Combine a FetchResult and a list of aggregations into one dict.

    Calls compute() on each aggregation without checking its type; each
    one adds its own section under its own key.
    """
    summary: dict[str, Any] = {
        "source_url": source_url,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "records_downloaded": result.records_downloaded,
        "records_processed": len(result.shows),
        "records_skipped": result.records_skipped,
    }
    for aggregation in aggregations:
        logger.debug("Computing %s", aggregation.key)
        summary[aggregation.key] = aggregation.compute(result.shows)
    return summary


def write_summary(summary: dict[str, Any], path: Path) -> None:
    """Write the summary to a JSON file, creating its folder if needed.

    Raises OutputError if the folder or file cannot be written.
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except OSError as error:
        raise OutputError(f"could not write {path}: {error.strerror}") from error
    logger.info("Wrote %s", path)
