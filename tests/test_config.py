"""Tests for reading the TOML settings file."""

from pathlib import Path

import pytest

from tvsummary import SettingsError, load_settings
from tvsummary.config import DEFAULT_CONFIG_PATH


def test_valid_file_is_read_into_settings(settings_file: Path) -> None:
    settings = load_settings(settings_file)
    assert settings.source_url == "https://example.invalid/shows"
    assert settings.timeout_seconds == 5.0
    assert settings.summary_path == Path("out") / "summary.json"
    assert settings.run_info_path == Path("out") / "run_info.json"
    assert settings.seed == 7
    assert settings.sample_size == 2
    assert settings.log_level == "INFO"


def test_settings_cannot_be_changed(settings_file: Path) -> None:
    settings = load_settings(settings_file)
    with pytest.raises(AttributeError):
        settings.seed = 1  # type: ignore[misc]  # proving frozen=True works


def test_the_repository_settings_file_is_valid() -> None:
    root = Path(__file__).resolve().parent.parent
    assert load_settings(root / DEFAULT_CONFIG_PATH).seed == 42


def test_missing_file_raises_settings_error(tmp_path: Path) -> None:
    with pytest.raises(SettingsError, match="settings file not found"):
        load_settings(tmp_path / "nope.toml")


def test_broken_toml_raises_settings_error(tmp_path: Path) -> None:
    path = tmp_path / "broken.toml"
    path.write_text("[source\nurl = ", encoding="utf-8")
    with pytest.raises(SettingsError, match="not valid TOML"):
        load_settings(path)


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        ("seed = 7", "", r"missing setting \[featured\] seed"),
        ("[logging]", "[log]", r"missing setting \[logging\] level"),
        ("seed = 7", 'seed = "seven"', "must be a whole number"),
        ("timeout_seconds = 5", "timeout_seconds = true", "must be a number"),
        ("timeout_seconds = 5", "timeout_seconds = 0", "must be above 0"),
        ("sample_size = 2", "sample_size = -1", "cannot be negative"),
        ('level = "info"', 'level = "loud"', "level must be one of"),
        ('folder = "out"', 'folder = ""', "must be non-empty text"),
    ],
)
def test_incomplete_or_bad_settings_raise(
    settings_file: Path, old: str, new: str, message: str
) -> None:
    text = settings_file.read_text(encoding="utf-8")
    settings_file.write_text(text.replace(old, new), encoding="utf-8")
    with pytest.raises(SettingsError, match=message):
        load_settings(settings_file)
