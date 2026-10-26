"""The record class: one clean TV show.

All the checks for missing or malformed fields live here, in
Show.__init__, so the rest of the program can trust every Show it gets.
"""

from datetime import datetime


class InvalidRecordError(ValueError):
    """Raised when a raw record cannot become a Show (not a dict, or no integer id)."""


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

    def __init__(self, raw):
        """Build a Show from one raw TVmaze record (a dict).

        Raises InvalidRecordError if the record is not a dict or has
        no integer "id", because such a record cannot be identified.
        """
        if not isinstance(raw, dict):
            raise InvalidRecordError(f"expected a dict but got a {type(raw).__name__}")
        show_id = raw.get("id")
        if not isinstance(show_id, int):
            raise InvalidRecordError(f"record has no integer id: {show_id!r}")

        self.id = show_id
        self.name = self._clean_name(raw.get("name"), show_id)
        self.genres = self._clean_genres(raw.get("genres"))
        self.rating = self._clean_rating(raw.get("rating"))
        self.language = self._clean_language(raw.get("language"))
        self.premiere_year = self._clean_premiere_year(raw.get("premiered"))
        self.channel_kind = self._clean_channel_kind(raw)

    def __str__(self):
        rating = f"{self.rating:.1f}" if self.rating is not None else "unrated"
        year = self.premiere_year if self.premiere_year is not None else "unknown year"
        return f"{self.name} ({year}, {rating})"

    def __repr__(self):
        return f"Show(id={self.id}, name={self.name!r})"

    # --- Cleaning helpers: each takes a raw value and returns a clean one ---

    @staticmethod
    def _clean_name(value, show_id):
        """Return the stripped name, or "Show #<id>" if it is missing or blank."""
        if isinstance(value, str) and value.strip():
            return value.strip()
        return f"Show #{show_id}"

    @staticmethod
    def _clean_genres(value):
        """Return the genres as a frozenset of non-empty strings."""
        if not isinstance(value, list):
            return frozenset()
        return frozenset(g.strip() for g in value if isinstance(g, str) and g.strip())

    @staticmethod
    def _clean_rating(value):
        """Return rating["average"] as a float, or None if it is not a number."""
        if not isinstance(value, dict):
            return None
        average = value.get("average")
        if isinstance(average, bool) or not isinstance(average, (int, float)):
            return None
        return float(average)

    @staticmethod
    def _clean_language(value):
        """Return the stripped language, or None if missing or blank."""
        if isinstance(value, str) and value.strip():
            return value.strip()
        return None

    @staticmethod
    def _clean_premiere_year(value):
        """Return the year from a "YYYY-MM-DD" date, or None if malformed."""
        if not isinstance(value, str):
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").year
        except ValueError:
            return None

    @staticmethod
    def _clean_channel_kind(raw):
        """Return "network", "web" or None depending on where the show airs."""
        for kind, key in (("network", "network"), ("web", "webChannel")):
            channel = raw.get(key)
            if isinstance(channel, dict) and channel.get("name"):
                return kind
        return None
