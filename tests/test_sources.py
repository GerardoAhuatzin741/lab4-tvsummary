"""Tests for the source module. requests.get is replaced, so no network is used."""

from collections.abc import Callable
from typing import Any

import pytest
import requests

from tvsummary import sources
from tvsummary.errors import ResponseShapeError, SourceError, TvSummaryError
from tvsummary.sources import TVMazeSource


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


@pytest.mark.parametrize(
    ("raised", "message"),
    [
        (requests.ConnectionError("no network"), "reach the server"),
        (requests.Timeout("slow"), "did not respond within 1 seconds"),
        (requests.TooManyRedirects("loop"), "TooManyRedirects"),
    ],
)
def test_network_failures_become_source_errors(
    monkeypatch: pytest.MonkeyPatch, raised: Exception, message: str
) -> None:
    def fake_get(*args: Any, **kwargs: Any) -> None:
        raise raised

    monkeypatch.setattr(sources.requests, "get", fake_get)
    with pytest.raises(SourceError, match=message) as caught:
        TVMazeSource("https://example.invalid", timeout=1).fetch()
    assert caught.value.__cause__ is raised


def test_http_error_status_becomes_a_source_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = requests.Response()
    response.status_code = 503
    monkeypatch.setattr(sources.requests, "get", lambda *a, **k: response)
    with pytest.raises(SourceError, match="HTTP 503"):
        TVMazeSource("https://example.invalid", timeout=1).fetch()


@pytest.mark.parametrize(
    ("response", "message"),
    [
        (FakeResponse({"oops": 1}), "JSON list of shows but got a dict"),
        (FakeResponse(bad_json=True), "not valid JSON"),
    ],
)
def test_bad_bodies_become_response_shape_errors(
    monkeypatch: pytest.MonkeyPatch, response: FakeResponse, message: str
) -> None:
    monkeypatch.setattr(sources.requests, "get", lambda *a, **k: response)
    with pytest.raises(ResponseShapeError, match=message):
        TVMazeSource("https://example.invalid", timeout=1).fetch()


def test_every_package_error_shares_one_base_class() -> None:
    assert issubclass(SourceError, TvSummaryError)
    assert issubclass(ResponseShapeError, TvSummaryError)
