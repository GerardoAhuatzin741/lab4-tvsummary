"""Tests for the Aggregation subclasses, using handmade Show objects only."""

import unittest

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


def make_show(
    show_id,
    name,
    genres=(),
    rating=None,
    language="English",
    premiered="2010-01-01",
    network="ABC",
    web=None,
):
    """Build a Show from a small handmade record."""
    return Show(
        {
            "id": show_id,
            "name": name,
            "genres": list(genres),
            "rating": {"average": rating},
            "language": language,
            "premiered": premiered,
            "network": {"name": network} if network else None,
            "webChannel": {"name": web} if web else None,
        }
    )


SHOWS = [
    make_show(1, "Alpha", ["Drama", "Crime"], 9.0, premiered="1995-03-01"),
    make_show(2, "Bravo", ["Drama"], 8.0, language="Japanese", premiered="2004-01-01"),
    make_show(
        3, "Charlie", [], None, premiered="bad date", network=None, web="Netflix"
    ),
    make_show(4, "Delta", ["Comedy"], 9.0, language=None, network=None),
]


class AggregationTests(unittest.TestCase):
    def test_shows_per_genre_most_common_first(self):
        self.assertEqual(
            ShowsPerGenre().compute(SHOWS),
            {"Drama": 2, "Comedy": 1, "Crime": 1},
        )

    def test_average_rating_ignores_unrated_shows(self):
        self.assertEqual(
            AverageRatingByLanguage().compute(SHOWS),
            {
                "English": {
                    "average_rating": 9.0,
                    "rated_shows": 1,
                    "unrated_shows": 1,
                },
                "Japanese": {
                    "average_rating": 8.0,
                    "rated_shows": 1,
                    "unrated_shows": 0,
                },
            },
        )

    def test_shows_per_decade_skips_bad_dates(self):
        self.assertEqual(
            ShowsPerDecade().compute(SHOWS),
            {"1990s": 1, "2000s": 1, "2010s": 1},
        )

    def test_top_rated_breaks_ties_by_name_and_respects_limit(self):
        self.assertEqual(
            TopRatedShows(limit=2).compute(SHOWS),
            [{"name": "Alpha", "rating": 9.0}, {"name": "Delta", "rating": 9.0}],
        )

    def test_data_quality_counts(self):
        self.assertEqual(
            DataQuality().compute(SHOWS),
            {
                "no_genres": 1,
                "no_rating": 1,
                "no_language": 1,
                "no_valid_premiere_date": 1,
                "web_channel_only": 1,
                "no_network_or_web_channel": 1,
            },
        )

    def test_every_default_aggregation_is_called_the_same_way(self):
        aggregations = default_aggregations()
        self.assertTrue(all(isinstance(a, Aggregation) for a in aggregations))
        results = {a.key: a.compute(SHOWS) for a in aggregations}
        self.assertEqual(
            list(results),
            [
                "shows_per_genre",
                "average_rating_by_language",
                "shows_per_decade",
                "top_rated_shows",
                "data_quality",
            ],
        )

    def test_base_class_must_be_overridden(self):
        with self.assertRaises(NotImplementedError):
            Aggregation().compute(SHOWS)

    def test_empty_list_gives_empty_results(self):
        self.assertEqual(ShowsPerGenre().compute([]), {})
        self.assertEqual(TopRatedShows().compute([]), [])


if __name__ == "__main__":
    unittest.main()
