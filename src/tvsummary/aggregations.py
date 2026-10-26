"""The summaries, one class each, all sharing the Aggregation base class.

Every aggregation takes a list of Show objects and returns a result that
can be written as JSON. None of them download, print or write anything.
"""

from typing import Any

from .config import TOP_RATED_LIMIT
from .models import Show


class Aggregation:
    """Base class for one section of the summary.

    Subclasses set `key` (the section's name in summary.json) and
    override compute(). Code that builds the summary only calls
    compute(), so it never needs to know which subclass it has.
    """

    key: str = "aggregation"

    def __init__(self, key: str | None = None) -> None:
        """Optionally override the section name used in the summary."""
        if key is not None:
            self.key = key

    def compute(self, shows: list[Show]) -> Any:
        """Return this section's result for a list of shows."""
        raise NotImplementedError(f"{type(self).__name__} must override compute()")

    def __str__(self) -> str:
        return f"{type(self).__name__} -> {self.key}"


class ShowsPerGenre(Aggregation):
    """How many shows list each genre; a show counts once per genre.

    Shows with no genres are left out here and reported in DataQuality.
    The result is ordered from most to least common genre.
    """

    key = "shows_per_genre"

    def compute(self, shows: list[Show]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for show in shows:
            for genre in show.genres:
                counts[genre] = counts.get(genre, 0) + 1
        return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


class AverageRatingByLanguage(Aggregation):
    """Average rating per language, using only shows that have a rating.

    Unrated shows are counted separately instead of being treated as zero,
    and a language with no rated shows gets an average of None.
    """

    key = "average_rating_by_language"

    def compute(self, shows: list[Show]) -> dict[str, dict[str, Any]]:
        ratings: dict[str, list[float]] = {}
        unrated: dict[str, int] = {}
        for show in shows:
            if show.language is None:
                continue
            if show.rating is None:
                unrated[show.language] = unrated.get(show.language, 0) + 1
            else:
                ratings.setdefault(show.language, []).append(show.rating)

        return {
            language: {
                "average_rating": (
                    round(sum(ratings[language]) / len(ratings[language]), 2)
                    if language in ratings
                    else None
                ),
                "rated_shows": len(ratings.get(language, [])),
                "unrated_shows": unrated.get(language, 0),
            }
            for language in sorted(set(ratings) | set(unrated))
        }


class ShowsPerDecade(Aggregation):
    """How many shows premiered in each decade, e.g. {"1990s": 12}.

    Shows with a missing or malformed premiere date are left out.
    """

    key = "shows_per_decade"

    def compute(self, shows: list[Show]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for show in shows:
            if show.premiere_year is None:
                continue
            decade = f"{show.premiere_year // 10 * 10}s"
            counts[decade] = counts.get(decade, 0) + 1
        return dict(sorted(counts.items()))


class TopRatedShows(Aggregation):
    """The highest-rated shows as a list of {"name", "rating"} dicts.

    Ties are broken alphabetically so the output is stable between runs.
    """

    key = "top_rated_shows"

    def __init__(self, limit: int = TOP_RATED_LIMIT, key: str | None = None) -> None:
        """Keep at most `limit` shows in the list."""
        super().__init__(key)
        self.limit = limit

    def compute(self, shows: list[Show]) -> list[dict[str, Any]]:
        rated = [(show.rating, show.name) for show in shows if show.rating is not None]
        rated.sort(key=lambda pair: (-pair[0], pair[1]))
        return [
            {"name": name, "rating": rating} for rating, name in rated[: self.limit]
        ]


class DataQuality(Aggregation):
    """How many shows have each kind of missing or malformed field."""

    key = "data_quality"

    def compute(self, shows: list[Show]) -> dict[str, int]:
        channel_kinds = [show.channel_kind for show in shows]
        return {
            "no_genres": sum(1 for s in shows if not s.genres),
            "no_rating": sum(1 for s in shows if s.rating is None),
            "no_language": sum(1 for s in shows if s.language is None),
            "no_valid_premiere_date": sum(1 for s in shows if s.premiere_year is None),
            "web_channel_only": channel_kinds.count("web"),
            "no_network_or_web_channel": channel_kinds.count(None),
        }


def default_aggregations() -> list[Aggregation]:
    """The aggregations in the order they appear in summary.json."""
    return [
        ShowsPerGenre(),
        AverageRatingByLanguage(),
        ShowsPerDecade(),
        TopRatedShows(),
        DataQuality(),
    ]
