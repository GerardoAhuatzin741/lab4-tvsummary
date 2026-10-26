"""tvsummary: summarize TV shows from the TVmaze public API into a JSON report."""

from .aggregations import (
    Aggregation,
    AverageRatingByLanguage,
    DataQuality,
    FeaturedShows,
    ShowsPerDecade,
    ShowsPerGenre,
    TopRatedShows,
    default_aggregations,
)
from .config import DEFAULT_CONFIG_PATH, Settings, load_settings
from .errors import (
    InvalidRecordError,
    OutputError,
    ResponseShapeError,
    SettingsError,
    SourceError,
    TvSummaryError,
)
from .models import Show
from .report import build_run_info, build_summary, write_json
from .sources import FetchResult, TVMazeSource

__version__ = "1.0.0"

__all__ = [
    "DEFAULT_CONFIG_PATH",
    "Aggregation",
    "AverageRatingByLanguage",
    "DataQuality",
    "FeaturedShows",
    "FetchResult",
    "InvalidRecordError",
    "OutputError",
    "ResponseShapeError",
    "Settings",
    "SettingsError",
    "Show",
    "ShowsPerDecade",
    "ShowsPerGenre",
    "SourceError",
    "TVMazeSource",
    "TopRatedShows",
    "TvSummaryError",
    "build_run_info",
    "build_summary",
    "default_aggregations",
    "load_settings",
    "write_json",
]
