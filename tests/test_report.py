"""Tests for building and writing summary.json and run_info.json, using tmp_path."""

import json
from pathlib import Path

import pytest

from tvsummary import (
    OutputError,
    Settings,
    Show,
    build_run_info,
    build_summary,
    default_aggregations,
    write_json,
)
from tvsummary.sources import FetchResult


def test_summary_keeps_every_lab03_key_and_adds_featured_shows(
    sample_shows: list[Show], settings: Settings
) -> None:
    result = FetchResult(sample_shows, records_downloaded=6, records_skipped=2)
    summary = build_summary(result, default_aggregations(settings), "https://x.invalid")
    assert list(summary) == [
        "source_url",
        "generated_at",
        "records_downloaded",
        "records_processed",
        "records_skipped",
        "shows_per_genre",
        "average_rating_by_language",
        "shows_per_decade",
        "top_rated_shows",
        "data_quality",
        "featured_shows",
    ]
    assert summary["records_processed"] == 4
    assert summary["records_skipped"] == 2


def test_write_json_creates_the_folder(tmp_path: Path) -> None:
    path = tmp_path / "out" / "summary.json"
    write_json({"name": "Stargate SG·1"}, path)
    assert json.loads(path.read_text(encoding="utf-8")) == {"name": "Stargate SG·1"}


def test_unwritable_path_raises_output_error(tmp_path: Path) -> None:
    blocker = tmp_path / "not_a_folder"
    blocker.write_text("a file where a folder should be", encoding="utf-8")
    with pytest.raises(OutputError, match="could not write"):
        write_json({"a": 1}, blocker / "summary.json")


def test_run_info_records_settings_and_versions(
    settings: Settings, settings_file: Path
) -> None:
    info = build_run_info(settings, settings_file)
    assert info["settings"]["seed"] == 42
    assert info["settings"]["sample_size"] == 2
    assert info["python_version"].count(".") == 2
    assert set(info["package_versions"]) == {
        "tvsummary",
        "requests",
        "pytest",
        "mypy",
        "ruff",
    }
