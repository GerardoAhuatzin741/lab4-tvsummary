"""The record class: one clean TV show.

All the checks for missing or malformed fields live here, in
Show.__init__, so the rest of the program can trust every Show it gets.
"""

from datetime import datetime
from typing import Any

from .errors import InvalidRecordError


class Show:
    """One TV show from TVmaze, with every field already cleaned.

    A field that is missing or malformed becomes None (or an empty set
    for genres) instead of a guess, so later code never has to check
    the raw data again.

    Attributes:
        id: the show's integer TVmaze id.
        name: the show's name, or "Show #<id>" if the name is missing.
        genres: a frozenset of non-empty genre names (may be empty).
        rating: the average rating as a float, or None if unrated.
        language: the language, or None if missing or blank.
        premiere_year: the year it premiered, or None if missing or malformed.
        channel_kind: "network", "web", or None if it has neither.
    """

    def __init__(self, raw: Any) -> None:
        """Build a Show from one raw TVmaze record (a dict).

        Raises InvalidRecordError if the record is not a dict or has
        no integer "id", because such a record cannot be identified.
        """
        problem = self.problem_with(raw)
        if problem is not None:
            raise InvalidRecordError(problem)

        self.id: int = raw["id"]
        self.name: str = self._clean_name(raw.get("name"), self.id)
        self.genres: frozenset[str] = self._clean_genres(raw.get("genres"))
        self.rating: float | None = self._clean_rating(raw.get("rating"))
        self.language: str | None = self._clean_language(raw.get("language"))
        self.premiere_year: int | None = self._clean_premiere_year(raw.get("premiered"))
        self.channel_kind: str | None = self._clean_channel_kind(raw)

    def __str__(self) -> str:
        rating = f"{self.rating:.1f}" if self.rating is not None else "unrated"
        year = self.premiere_year if self.premiere_year is not None else "unknown year"
        return f"{self.name} ({year}, {rating})"

    def __repr__(self) -> str:
        return f"Show(id={self.id}, name={self.name!r})"

    @staticmethod
    def problem_with(raw: Any) -> str | None:
        """Return why a raw record cannot become a Show, or None if it can.

        A usable record is a dict with an integer "id". Callers can check
        this first and skip bad records without catching an exception.
        """
        if not isinstance(raw, dict):
            return f"expected a dict but got a {type(raw).__name__}"
        show_id = raw.get("id")
        if not isinstance(show_id, int):
            return f"record has no integer id: {show_id!r}"
        return None

    # --- Cleaning helpers: each takes a raw value and returns a clean one ---

    @staticmethod
    def _clean_name(value: Any, show_id: int) -> str:
        """Return the stripped name, or "Show #<id>" if it is missing or blank."""
        if isinstance(value, str) and value.strip():
            return value.strip()
        return f"Show #{show_id}"

    @staticmethod
    def _clean_genres(value: Any) -> frozenset[str]:
        """Return the genres as a frozenset of non-empty strings."""
        if not isinstance(value, list):
            return frozenset()
        return frozenset(g.strip() for g in value if isinstance(g, str) and g.strip())

    @staticmethod
    def _clean_rating(value: Any) -> float | None:
        """Return rating["average"] as a float, or None if it is not a number."""
        if not isinstance(value, dict):
            return None
        average = value.get("average")
        if isinstance(average, bool) or not isinstance(average, (int, float)):
            return None
        return float(average)

    @staticmethod
    def _clean_language(value: Any) -> str | None:
        """Return the stripped language, or None if missing or blank."""
        if isinstance(value, str) and value.strip():
            return value.strip()
        return None

    @staticmethod
    def _clean_premiere_year(value: Any) -> int | None:
        """Return the year from a "YYYY-MM-DD" date, or None if malformed."""
        if not isinstance(value, str):
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").year
        except ValueError:
            return None

    @staticmethod
    def _clean_channel_kind(raw: dict[str, Any]) -> str | None:
        """Return "network", "web" or None depending on where the show airs."""
        for kind, key in (("network", "network"), ("web", "webChannel")):
            channel = raw.get(key)
            if isinstance(channel, dict) and channel.get("name"):
                return kind
        return None
