"""Building the summary dict and writing it to disk."""

import json
from datetime import datetime, timezone


def build_summary(result, aggregations, source_url):
    """Combine a FetchResult and a list of aggregations into one dict.

    Calls compute() on each aggregation without checking its type; each
    one adds its own section under its own key.
    """
    summary = {
        "source_url": source_url,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "records_downloaded": result.records_downloaded,
        "records_processed": len(result.shows),
        "records_skipped": result.records_skipped,
    }
    for aggregation in aggregations:
        summary[aggregation.key] = aggregation.compute(result.shows)
    return summary


def write_summary(summary, path):
    """Write the summary to a JSON file, creating its folder if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
