"""Tests for the Show class and for TVMazeSource.parse, using handmade records only."""

import unittest

from tvsummary import InvalidRecordError, Show, TVMazeSource


def make_record(**overrides):
    """Return a complete, valid raw record, with any fields replaced."""
    record = {
        "id": 1,
        "name": "Test Show",
        "genres": ["Drama", "Comedy"],
        "rating": {"average": 8.5},
        "language": "English",
        "premiered": "2010-05-01",
        "network": {"name": "ABC"},
        "webChannel": None,
    }
    record.update(overrides)
    return record


class ShowCleaningTests(unittest.TestCase):
    """Show.__init__ turns raw values into clean ones."""

    def test_complete_record_keeps_every_field(self):
        show = Show(make_record())
        self.assertEqual(show.id, 1)
        self.assertEqual(show.name, "Test Show")
        self.assertEqual(show.genres, {"Drama", "Comedy"})
        self.assertEqual(show.rating, 8.5)
        self.assertEqual(show.language, "English")
        self.assertEqual(show.premiere_year, 2010)
        self.assertEqual(show.channel_kind, "network")

    def test_missing_name_falls_back_to_id(self):
        self.assertEqual(Show(make_record(id=7, name="  ")).name, "Show #7")

    def test_genres_drop_blanks_duplicates_and_non_strings(self):
        show = Show(make_record(genres=["Drama", " Drama ", "", None, 5]))
        self.assertEqual(show.genres, {"Drama"})

    def test_genres_that_are_not_a_list_become_empty(self):
        self.assertEqual(Show(make_record(genres="Drama")).genres, frozenset())

    def test_bad_ratings_become_none(self):
        for rating in (
            None,
            {"average": None},
            {"average": "8.5"},
            {"average": True},
            8.5,
        ):
            with self.subTest(rating=rating):
                self.assertIsNone(Show(make_record(rating=rating)).rating)

    def test_integer_rating_becomes_float(self):
        rating = Show(make_record(rating={"average": 9})).rating
        self.assertEqual(rating, 9.0)
        self.assertIsInstance(rating, float)

    def test_bad_language_becomes_none(self):
        for language in (None, "", "   ", 3):
            with self.subTest(language=language):
                self.assertIsNone(Show(make_record(language=language)).language)

    def test_bad_premiere_dates_become_none(self):
        for premiered in (None, "", "2010", "2010-13-01", "not a date", 2010):
            with self.subTest(premiered=premiered):
                self.assertIsNone(Show(make_record(premiered=premiered)).premiere_year)

    def test_web_only_show(self):
        show = Show(make_record(network=None, webChannel={"name": "Netflix"}))
        self.assertEqual(show.channel_kind, "web")

    def test_no_channel_at_all(self):
        show = Show(make_record(network=None, webChannel={"name": ""}))
        self.assertIsNone(show.channel_kind)

    def test_record_without_integer_id_is_rejected(self):
        for raw in ({"name": "No id"}, {"id": "12"}, ["not", "a", "dict"], None):
            with self.subTest(raw=raw):
                with self.assertRaises(InvalidRecordError):
                    Show(raw)

    def test_str_is_readable(self):
        self.assertEqual(str(Show(make_record())), "Test Show (2010, 8.5)")
        unrated = Show(make_record(rating=None, premiered=None))
        self.assertEqual(str(unrated), "Test Show (unknown year, unrated)")


class ParseTests(unittest.TestCase):
    """TVMazeSource.parse builds Show objects without touching the network."""

    def test_drops_invalid_and_repeated_records(self):
        raw = [
            make_record(id=1),
            make_record(id=1),
            {"name": "no id"},
            "junk",
            make_record(id=2),
        ]
        shows, skipped = TVMazeSource.parse(raw)
        self.assertEqual([show.id for show in shows], [1, 2])
        self.assertEqual(skipped, 3)


if __name__ == "__main__":
    unittest.main()
