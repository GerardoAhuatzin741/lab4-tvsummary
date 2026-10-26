"""One test per aggregation class, using the hand-made shows from conftest.py."""

import pytest

from tvsummary import (
    Aggregation,
    AverageRatingByLanguage,
    DataQuality,
    Show,
    ShowsPerDecade,
    ShowsPerGenre,
    TopRatedShows,
    default_aggregations,
)


def test_shows_per_genre_most_common_first(sample_shows: list[Show]) -> None:
    result = ShowsPerGenre().compute(sample_shows)
    assert result == {"Drama": 2, "Comedy": 1, "Crime": 1}
    assert list(result) == ["Drama", "Comedy", "Crime"]


def test_average_rating_ignores_unrated_shows(sample_shows: list[Show]) -> None:
    assert AverageRatingByLanguage().compute(sample_shows) == {
        "English": {"average_rating": 9.0, "rated_shows": 1, "unrated_shows": 1},
        "Japanese": {"average_rating": 8.0, "rated_shows": 1, "unrated_shows": 0},
    }


def test_shows_per_decade_skips_bad_dates(sample_shows: list[Show]) -> None:
    assert ShowsPerDecade().compute(sample_shows) == {
        "1990s": 1,
        "2000s": 1,
        "2010s": 1,
    }


def test_top_rated_breaks_ties_by_name(sample_shows: list[Show]) -> None:
    assert TopRatedShows(limit=2).compute(sample_shows) == [
        {"name": "Alpha", "rating": 9.0},
        {"name": "Delta", "rating": 9.0},
    ]


def test_data_quality_counts(sample_shows: list[Show]) -> None:
    assert DataQuality().compute(sample_shows) == {
        "no_genres": 1,
        "no_rating": 1,
        "no_language": 1,
        "no_valid_premiere_date": 1,
        "web_channel_only": 1,
        "no_network_or_web_channel": 1,
    }


def test_every_aggregation_is_called_the_same_way(sample_shows: list[Show]) -> None:
    aggregations = default_aggregations()
    assert all(isinstance(a, Aggregation) for a in aggregations)
    keys = [a.key for a in aggregations]
    results = {a.key: a.compute(sample_shows) for a in aggregations}
    assert list(results) == keys


def test_base_class_must_be_overridden(sample_shows: list[Show]) -> None:
    with pytest.raises(NotImplementedError, match="must override compute"):
        Aggregation().compute(sample_shows)


def test_empty_input_gives_empty_results() -> None:
    assert ShowsPerGenre().compute([]) == {}
    assert TopRatedShows().compute([]) == []
