"""tvsummary: summarize TV shows from the TVmaze public API into a JSON report."""

from .aggregations import (
    Aggregation,
    AverageRatingByLanguage,
    DataQuality,
    ShowsPerDecade,
    ShowsPerGenre,
    TopRatedShows,
    default_aggregations,
)
from .models import InvalidRecordError, Show
from .report import build_summary, write_summary
from .sources import DownloadError, FetchResult, TVMazeSource

__version__ = "1.0.0"

__all__ = [
    "Aggregation",
    "AverageRatingByLanguage",
    "DataQuality",
    "DownloadError",
    "FetchResult",
    "InvalidRecordError",
    "Show",
    "ShowsPerDecade",
    "ShowsPerGenre",
    "TVMazeSource",
    "TopRatedShows",
    "build_summary",
    "default_aggregations",
    "write_summary",
]
