"""Getting the data. This is the only module that imports requests."""

import logging
from dataclasses import dataclass
from typing import Any

import requests

from .errors import ResponseShapeError, SourceError
from .models import Show

logger = logging.getLogger(__name__)


@dataclass
class FetchResult:
    """What one download produced: the clean shows and how many were dropped."""

    shows: list[Show]
    records_downloaded: int
    records_skipped: int


class TVMazeSource:
    """Downloads TV show records from TVmaze and turns them into Show objects."""

    def __init__(self, url: str, timeout: float) -> None:
        """Remember where to download from and how long to wait."""
        self.url = url
        self.timeout = timeout

    def fetch(self) -> FetchResult:
        """Download the records and return a FetchResult of Show objects.

        Raises SourceError or ResponseShapeError with a readable message.
        """
        logger.info("Downloading shows from %s", self.url)
        raw_records = self.fetch_raw()
        logger.debug("%s records arrived", len(raw_records))
        shows, skipped = self.parse(raw_records)
        logger.info("Kept %s shows, skipped %s", len(shows), skipped)
        return FetchResult(shows, len(raw_records), skipped)

    def fetch_raw(self) -> list[Any]:
        """Download the records and return them as a list of raw dicts.

        Raises SourceError if the request fails or the server answers with
        an error status, and ResponseShapeError if the body is not a JSON list.
        """
        try:
            response = requests.get(self.url, timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.Timeout as error:
            raise SourceError(
                f"the server did not respond within {self.timeout} seconds."
            ) from error
        except requests.exceptions.ConnectionError as error:
            raise SourceError(
                "could not reach the server. Check your internet connection."
            ) from error
        except requests.exceptions.HTTPError as error:
            status = error.response.status_code if error.response is not None else "?"
            raise SourceError(f"the server returned HTTP {status}.") from error
        except requests.exceptions.RequestException as error:
            raise SourceError(
                f"the request failed ({type(error).__name__})."
            ) from error

        try:
            data: Any = response.json()
        except ValueError as error:
            raise ResponseShapeError("the response was not valid JSON.") from error

        if not isinstance(data, list):
            raise ResponseShapeError(
                f"expected a JSON list of shows but got a {type(data).__name__}."
            )
        return data

    @staticmethod
    def parse(raw_records: list[Any]) -> tuple[list[Show], int]:
        """Turn raw records into Show objects, dropping bad and repeated ones.

        Returns a tuple (shows, skipped), where skipped counts the records
        that were not usable or repeated an id already seen.
        """
        seen_ids: set[int] = set()
        shows: list[Show] = []
        skipped = 0
        for position, raw in enumerate(raw_records):
            problem = Show.problem_with(raw)
            if problem is not None:
                logger.warning("Skipping record %s: %s", position, problem)
                skipped += 1
                continue
            show = Show(raw)
            if show.id in seen_ids:
                logger.warning("Skipping record %s: repeated id %s", position, show.id)
                skipped += 1
                continue
            seen_ids.add(show.id)
            shows.append(show)
        return shows, skipped
