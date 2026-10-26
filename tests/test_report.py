"""Tests for building and writing the summary, using tmp_path for the output."""

import json
from pathlib import Path

from tvsummary import Show, build_summary, default_aggregations, write_summary
from tvsummary.sources import FetchResult


def test_summary_keys_and_counts(sample_shows: list[Show]) -> None:
    result = FetchResult(sample_shows, records_downloaded=6, records_skipped=2)
    summary = build_summary(result, default_aggregations(), "https://example.invalid")
    assert list(summary)[:5] == [
        "source_url",
        "generated_at",
        "records_downloaded",
        "records_processed",
        "records_skipped",
    ]
    assert summary["records_processed"] == 4
    assert summary["records_skipped"] == 2


def test_write_summary_creates_folder(tmp_path: Path, sample_shows: list[Show]) -> None:
    result = FetchResult(sample_shows, records_downloaded=4, records_skipped=0)
    summary = build_summary(result, default_aggregations(), "https://example.invalid")
    path = tmp_path / "out" / "summary.json"
    write_summary(summary, path)
    assert json.loads(path.read_text(encoding="utf-8")) == summary
