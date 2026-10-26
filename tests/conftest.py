"""Shared fixtures: hand-made records and shows, so no test needs the network."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from tvsummary import Settings, Show

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


VALID_TOML = """
[source]
url = "https://example.invalid/shows"
timeout_seconds = 5

[output]
folder = "out"

[summary]
top_rated_limit = 3

[featured]
seed = 7
sample_size = 2

[logging]
level = "info"
"""


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    """Settings that write into this test's own temporary folder."""
    return Settings(
        source_url="https://example.invalid/shows",
        timeout_seconds=1.0,
        output_folder=tmp_path / "processed",
        top_rated_limit=10,
        seed=42,
        sample_size=2,
        log_level="INFO",
    )


@pytest.fixture
def settings_file(tmp_path: Path) -> Path:
    """A complete, valid settings file in a temporary folder."""
    path = tmp_path / "tvsummary.toml"
    path.write_text(VALID_TOML, encoding="utf-8")
    return path
