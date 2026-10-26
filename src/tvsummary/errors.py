"""The package's own exceptions.

Every failure the program expects is a subclass of TvSummaryError, so
main() can catch them all in one place and show a clear message.
"""


class TvSummaryError(Exception):
    """Base class for every error this package raises on purpose."""


class SourceError(TvSummaryError):
    """The data could not be downloaded (no network, timeout, HTTP error)."""


class ResponseShapeError(TvSummaryError):
    """The download worked, but the body was not the list of shows expected."""


class InvalidRecordError(TvSummaryError):
    """One raw record cannot become a Show (not a dict, or no integer id)."""


class SettingsError(TvSummaryError):
    """The settings file is missing, unreadable, or has a missing or bad value."""


class OutputError(TvSummaryError):
    """The summary or run_info file could not be written."""
