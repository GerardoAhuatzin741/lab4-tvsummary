"""Shared fixtures: hand-made records and shows, so no test needs the network."""

from collections.abc import Callable
from typing import Any

import pytest

from tvsummary import Show

RawRecord = dict[str, Any]


def _raw(**overrides: Any) -> RawRecord:
    """Return a complete, valid raw TVmaze record with some fields replaced."""
    record: RawRecord = {
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


@pytest.fixture
def make_raw() -> Callable[..., RawRecord]:
    """A factory for raw records: make_raw(id=2, rating=None)."""
    return _raw


@pytest.fixture
def sample_shows() -> list[Show]:
    """Four shows that cover the awkward cases: no genres, no rating, bad date,
    web-only, no language, and a tie in rating."""
    return [
        Show(
            _raw(
                id=1,
                name="Alpha",
                genres=["Drama", "Crime"],
                rating={"average": 9.0},
                premiered="1995-03-01",
            )
        ),
        Show(
            _raw(
                id=2,
                name="Bravo",
                genres=["Drama"],
                rating={"average": 8.0},
                language="Japanese",
                premiered="2004-01-01",
            )
        ),
        Show(
            _raw(
                id=3,
                name="Charlie",
                genres=[],
                rating={"average": None},
                premiered="bad date",
                network=None,
                webChannel={"name": "Netflix"},
            )
        ),
        Show(
            _raw(
                id=4,
                name="Delta",
                genres=["Comedy"],
                rating={"average": 9.0},
                language=None,
                network=None,
            )
        ),
    ]
