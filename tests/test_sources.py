"""Tests for the source module. requests.get is replaced, so no network is used."""

from collections.abc import Callable
from typing import Any

import pytest
import requests

from tvsummary import sources
from tvsummary.sources import DownloadError, TVMazeSource


class FakeResponse:
    """Stands in for requests.Response with a fixed body."""

    def __init__(self, body: Any = None, bad_json: bool = False) -> None:
        self.body = body
        self.bad_json = bad_json

    def raise_for_status(self) -> None:
        return None

    def json(self) -> Any:
        if self.bad_json:
            raise ValueError("not json")
        return self.body


def test_parse_drops_invalid_and_repeated_records(
    make_raw: Callable[..., Any],
) -> None:
    raw = [make_raw(id=1), make_raw(id=1), {"name": "no id"}, "junk", make_raw(id=2)]
    shows, skipped = TVMazeSource.parse(raw)
    assert [show.id for show in shows] == [1, 2]
    assert skipped == 3


def test_fetch_returns_shows(
    monkeypatch: pytest.MonkeyPatch, make_raw: Callable[..., Any]
) -> None:
    body = [make_raw(id=1), make_raw(id=2), "junk"]
    monkeypatch.setattr(sources.requests, "get", lambda *a, **k: FakeResponse(body))
    result = TVMazeSource("https://example.invalid", timeout=1).fetch()
    assert [show.id for show in result.shows] == [1, 2]
    assert result.records_downloaded == 3
    assert result.records_skipped == 1


def test_a_failed_download_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(*args: Any, **kwargs: Any) -> None:
        raise requests.ConnectionError("no network")

    monkeypatch.setattr(sources.requests, "get", fake_get)
    with pytest.raises(DownloadError, match="connect"):
        TVMazeSource("https://example.invalid", timeout=1).fetch()


def test_a_response_that_is_not_a_list_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        sources.requests, "get", lambda *a, **k: FakeResponse({"oops": 1})
    )
    with pytest.raises(DownloadError, match="list"):
        TVMazeSource("https://example.invalid", timeout=1).fetch()
