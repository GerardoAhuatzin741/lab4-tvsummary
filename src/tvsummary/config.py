"""Reads config/tvsummary.toml into a frozen Settings object.

Every value the program uses comes from that file, so a run can be
repeated by keeping the file. A missing file, a missing value, or a value
of the wrong type raises SettingsError with the name of the setting.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import SettingsError

DEFAULT_CONFIG_PATH = Path("config") / "tvsummary.toml"

LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


@dataclass(frozen=True)
class Settings:
    """Every setting for one run. Frozen, so nothing can change it mid-run."""

    source_url: str
    timeout_seconds: float
    output_folder: Path
    top_rated_limit: int
    seed: int
    sample_size: int
    log_level: str

    @property
    def summary_path(self) -> Path:
        """Where summary.json is written."""
        return self.output_folder / "summary.json"

    @property
    def run_info_path(self) -> Path:
        """Where run_info.json is written, next to summary.json."""
        return self.output_folder / "run_info.json"

    def as_dict(self) -> dict[str, Any]:
        """The settings as plain JSON values, for run_info.json."""
        return {
            "source_url": self.source_url,
            "timeout_seconds": self.timeout_seconds,
            "output_folder": self.output_folder.as_posix(),
            "top_rated_limit": self.top_rated_limit,
            "seed": self.seed,
            "sample_size": self.sample_size,
            "log_level": self.log_level,
        }


def load_settings(path: Path = DEFAULT_CONFIG_PATH) -> Settings:
    """Read the TOML file at `path` and return a checked Settings object.

    Raises SettingsError if the file is missing, is not valid TOML, or has
    a missing or invalid setting.
    """
    try:
        with path.open("rb") as file:
            data = tomllib.load(file)
    except FileNotFoundError as error:
        raise SettingsError(f"settings file not found: {path}") from error
    except tomllib.TOMLDecodeError as error:
        raise SettingsError(
            f"settings file {path} is not valid TOML: {error}"
        ) from error
    except OSError as error:
        raise SettingsError(
            f"could not read settings file {path}: {error.strerror}"
        ) from error

    reader = _Reader(data, path)
    settings = Settings(
        source_url=reader.text("source", "url"),
        timeout_seconds=reader.number("source", "timeout_seconds"),
        output_folder=Path(reader.text("output", "folder")),
        top_rated_limit=reader.integer("summary", "top_rated_limit"),
        seed=reader.integer("featured", "seed"),
        sample_size=reader.integer("featured", "sample_size"),
        log_level=reader.text("logging", "level").upper(),
    )
    _check(settings, path)
    return settings


class _Reader:
    """Looks up one [section] key in the parsed TOML and checks its type."""

    def __init__(self, data: dict[str, Any], path: Path) -> None:
        """Keep the parsed file and its path for error messages."""
        self.data = data
        self.path = path

    def _get(self, section: str, key: str) -> Any:
        table = self.data.get(section)
        if not isinstance(table, dict) or key not in table:
            raise SettingsError(f"missing setting [{section}] {key} in {self.path}")
        return table[key]

    def text(self, section: str, key: str) -> str:
        """A non-empty string setting."""
        value = self._get(section, key)
        if not isinstance(value, str) or not value.strip():
            raise SettingsError(f"setting [{section}] {key} must be non-empty text")
        return value.strip()

    def integer(self, section: str, key: str) -> int:
        """A whole-number setting (true and false are not accepted)."""
        value = self._get(section, key)
        if isinstance(value, bool) or not isinstance(value, int):
            raise SettingsError(f"setting [{section}] {key} must be a whole number")
        return value

    def number(self, section: str, key: str) -> float:
        """A number setting, whole or decimal."""
        value = self._get(section, key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise SettingsError(f"setting [{section}] {key} must be a number")
        return float(value)


def _check(settings: Settings, path: Path) -> None:
    """Reject values that have the right type but make no sense."""
    if settings.timeout_seconds <= 0:
        raise SettingsError(f"[source] timeout_seconds must be above 0 in {path}")
    if settings.top_rated_limit < 1:
        raise SettingsError(f"[summary] top_rated_limit must be at least 1 in {path}")
    if settings.sample_size < 0:
        raise SettingsError(f"[featured] sample_size cannot be negative in {path}")
    if settings.log_level not in LOG_LEVELS:
        raise SettingsError(
            f"[logging] level must be one of {', '.join(LOG_LEVELS)} in {path}"
        )
