"""Tests for the Show record class."""

from collections.abc import Callable
from typing import Any

import pytest

from tvsummary import InvalidRecordError, Show


def test_complete_record_keeps_every_field(make_raw: Callable[..., Any]) -> None:
    show = Show(make_raw())
    assert show.id == 1
    assert show.name == "Test Show"
    assert show.genres == {"Drama", "Comedy"}
    assert show.rating == 8.5
    assert show.language == "English"
    assert show.premiere_year == 2010
    assert show.channel_kind == "network"


def test_missing_genre_list_becomes_empty(make_raw: Callable[..., Any]) -> None:
    raw = make_raw()
    del raw["genres"]
    assert Show(raw).genres == frozenset()


def test_missing_rating_becomes_none(make_raw: Callable[..., Any]) -> None:
    raw = make_raw()
    del raw["rating"]
    assert Show(raw).rating is None


@pytest.mark.parametrize(
    "rating",
    [None, {"average": None}, {"average": "8.5"}, {"average": True}, 8.5],
)
def test_malformed_ratings_become_none(
    make_raw: Callable[..., Any], rating: Any
) -> None:
    assert Show(make_raw(rating=rating)).rating is None


def test_integer_rating_becomes_float(make_raw: Callable[..., Any]) -> None:
    rating = Show(make_raw(rating={"average": 9})).rating
    assert rating == 9.0
    assert isinstance(rating, float)


def test_genres_drop_blanks_duplicates_and_non_strings(
    make_raw: Callable[..., Any],
) -> None:
    show = Show(make_raw(genres=["Drama", " Drama ", "", None, 5]))
    assert show.genres == {"Drama"}


@pytest.mark.parametrize(
    "premiered", [None, "", "2010", "2010-13-01", "not a date", 2010]
)
def test_malformed_premiere_dates_become_none(
    make_raw: Callable[..., Any], premiered: Any
) -> None:
    assert Show(make_raw(premiered=premiered)).premiere_year is None


@pytest.mark.parametrize("language", [None, "", "   ", 3])
def test_blank_language_becomes_none(
    make_raw: Callable[..., Any], language: Any
) -> None:
    assert Show(make_raw(language=language)).language is None


def test_missing_name_falls_back_to_id(make_raw: Callable[..., Any]) -> None:
    assert Show(make_raw(id=7, name="  ")).name == "Show #7"


def test_channel_kind(make_raw: Callable[..., Any]) -> None:
    web = Show(make_raw(network=None, webChannel={"name": "Netflix"}))
    neither = Show(make_raw(network=None, webChannel={"name": ""}))
    assert web.channel_kind == "web"
    assert neither.channel_kind is None


@pytest.mark.parametrize("raw", [{"name": "No id"}, {"id": "12"}, ["a"], None])
def test_record_without_integer_id_is_rejected(raw: Any) -> None:
    with pytest.raises(InvalidRecordError, match="id|dict"):
        Show(raw)


def test_str_is_readable(make_raw: Callable[..., Any]) -> None:
    assert str(Show(make_raw())) == "Test Show (2010, 8.5)"
    unrated = Show(make_raw(rating=None, premiered=None))
    assert str(unrated) == "Test Show (unknown year, unrated)"
