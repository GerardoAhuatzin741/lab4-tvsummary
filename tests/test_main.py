"""Tests of main(): exit codes, printed messages and the files a run writes."""

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
import requests

from tvsummary import sources
from tvsummary.main import main


class FakeResponse:
    """Stands in for requests.Response with a fixed list of records."""

    def __init__(self, body: list[Any]) -> None:
        self.body = body

    def raise_for_status(self) -> None:
        return None

    def json(self) -> list[Any]:
        return self.body


def test_missing_config_prints_error_and_returns_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = main(["--config", str(tmp_path / "missing.toml")])
    captured = capsys.readouterr()
    assert code == 1
    assert captured.out == ""
    error_lines = [
        line for line in captured.err.splitlines() if line.startswith("Error:")
    ]
    assert len(error_lines) == 1
    assert "settings file not found" in error_lines[0]
    assert "Traceback" not in captured.err


def test_failed_download_prints_error_returns_1_and_logs_it(
    monkeypatch: pytest.MonkeyPatch,
    settings_file: Path,
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    def fake_get(*args: Any, **kwargs: Any) -> None:
        raise requests.ConnectionError("no network")

    monkeypatch.setattr(sources.requests, "get", fake_get)
    code = main(["--config", str(settings_file)])
    captured = capsys.readouterr()
    assert code == 1
    assert "Error: could not reach the server" in captured.err
    assert "Traceback" not in captured.err
    assert any(
        record.levelname == "ERROR" and "could not reach" in record.getMessage()
        for record in caplog.records
    )


def test_successful_run_writes_both_files_and_returns_0(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    settings_file: Path,
    make_raw: Callable[..., Any],
    capsys: pytest.CaptureFixture[str],
) -> None:
    body = [make_raw(id=i, name=f"Show {i}") for i in range(1, 6)] + ["junk"]
    monkeypatch.setattr(sources.requests, "get", lambda *a, **k: FakeResponse(body))
    monkeypatch.chdir(tmp_path)  # the settings file writes to the relative "out"

    code = main(["--config", str(settings_file)])
    captured = capsys.readouterr()
    assert code == 0
    assert captured.out.strip() == (
        "Processed 5 shows (1 skipped). Summary written to out/summary.json."
    )

    summary = json.loads((tmp_path / "out" / "summary.json").read_text("utf-8"))
    run_info = json.loads((tmp_path / "out" / "run_info.json").read_text("utf-8"))
    assert summary["records_processed"] == 5
    assert len(summary["featured_shows"]) == 2
    assert run_info["settings"]["seed"] == 7


def test_two_runs_with_the_same_seed_feature_the_same_shows(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    settings_file: Path,
    make_raw: Callable[..., Any],
) -> None:
    body = [make_raw(id=i, name=f"Show {i}") for i in range(1, 30)]
    monkeypatch.setattr(sources.requests, "get", lambda *a, **k: FakeResponse(body))
    monkeypatch.chdir(tmp_path)
    summary_path = tmp_path / "out" / "summary.json"

    assert main(["--config", str(settings_file)]) == 0
    first = json.loads(summary_path.read_text("utf-8"))["featured_shows"]
    assert main(["--config", str(settings_file)]) == 0
    second = json.loads(summary_path.read_text("utf-8"))["featured_shows"]
    assert first == second
