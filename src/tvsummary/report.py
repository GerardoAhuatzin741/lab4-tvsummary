"""Building summary.json and run_info.json, and writing them to disk."""

import json
import logging
import platform
from collections.abc import Sequence
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from .aggregations import Aggregation
from .config import Settings
from .errors import OutputError
from .sources import FetchResult

logger = logging.getLogger(__name__)

TOOLS = ("tvsummary", "requests", "pytest", "mypy", "ruff")


def build_summary(
    result: FetchResult, aggregations: Sequence[Aggregation], source_url: str
) -> dict[str, Any]:
    """Combine a FetchResult and a list of aggregations into one dict.

    Calls compute() on each aggregation without checking its type; each
    one adds its own section under its own key.
    """
    summary: dict[str, Any] = {
        "source_url": source_url,
        "generated_at": _now(),
        "records_downloaded": result.records_downloaded,
        "records_processed": len(result.shows),
        "records_skipped": result.records_skipped,
    }
    for aggregation in aggregations:
        logger.debug("Computing %s", aggregation.key)
        summary[aggregation.key] = aggregation.compute(result.shows)
    return summary


def build_run_info(settings: Settings, config_path: Path) -> dict[str, Any]:
    """Record what is needed to repeat this run: settings and versions."""
    return {
        "generated_at": _now(),
        "config_file": config_path.as_posix(),
        "settings": settings.as_dict(),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "package_versions": {name: _version_of(name) for name in TOOLS},
    }


def write_json(data: dict[str, Any], path: Path) -> None:
    """Write `data` as indented JSON, creating the folder if needed.

    Raises OutputError if the folder or file cannot be written.
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except OSError as error:
        raise OutputError(f"could not write {path}: {error.strerror}") from error
    logger.info("Wrote %s", path)


def _now() -> str:
    """The current UTC time, to the second, as an ISO 8601 string."""
    return datetime.now(UTC).isoformat(timespec="seconds")


def _version_of(name: str) -> str:
    """The installed version of a package, or "not installed"."""
    try:
        return version(name)
    except PackageNotFoundError:
        return "not installed"
