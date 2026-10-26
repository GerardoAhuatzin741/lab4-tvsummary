# TV Show Summary (tvsummary)

This package downloads a page of TV shows from the free TVmaze API and writes a JSON report: shows per genre, average rating per language, shows per decade, the top-rated shows, missing data, and a short list of featured shows picked with a fixed seed. It is my Lab 03 package made reliable, with tests, its own errors, logging, type hints, linting and a settings file.

## Setup

    conda env create -f environment.yml
    conda activate tvsummary
    pip install -r requirements.txt
    pip install -e .

## Run

    python -m tvsummary.main
    python -m tvsummary.main --config config/tvsummary.toml

Run it from the repository root. A run writes `data/processed/summary.json` and `data/processed/run_info.json`, and prints one line such as `Processed 240 shows (0 skipped). Summary written to data/processed/summary.json.` Log messages go to standard error.

## Check it

    python -m ruff format --check .
    python -m ruff check .
    python -m mypy
    python -m pytest

All four pass. The settings for each tool are in `pyproject.toml`.

## Settings

Every setting is in `config/tvsummary.toml`:

- `[source] url`: the TVmaze page to download.
- `[source] timeout_seconds`: how long to wait for the server before giving up.
- `[output] folder`: where `summary.json` and `run_info.json` are written.
- `[summary] top_rated_limit`: how many shows the `top_rated_shows` list keeps.
- `[featured] seed`: the seed for `random.Random`, which picks the featured shows.
- `[featured] sample_size`: how many show names go in `featured_shows`.
- `[logging] level`: the lowest log level shown (DEBUG, INFO, WARNING, ERROR or CRITICAL).

## Errors and exit codes

All the errors below are subclasses of `TvSummaryError` in `errors.py`. Only `main()` catches them.

| Error class | When it is raised | What the user sees |
|---|---|---|
| `SettingsError` | The settings file is missing, is not valid TOML, or has a missing or invalid value | `Error: settings file not found: nope.toml` (or the name of the bad setting) |
| `SourceError` | No connection, a timeout, an HTTP error status, or another request failure | `Error: could not reach the server. Check your internet connection.` |
| `ResponseShapeError` | The body is not valid JSON, is not a list, or has no usable show records | `Error: expected a JSON list of shows but got a dict.` |
| `OutputError` | `summary.json` or `run_info.json` cannot be written | `Error: could not write data/processed/summary.json: Permission denied` |
| `InvalidRecordError` | `Show()` is given a record that is not a dict or has no integer id | Nothing: the source checks `Show.problem_with()` first, logs a WARNING and skips the record |

Exit code **0** means the run finished and both files were written. Exit code **1** means an expected failure stopped the run: an ERROR is logged and one line starting with `Error:` is printed to standard error, with no traceback.

## Reproducing a run

The seed is in `config/tvsummary.toml`, under `[featured] seed`. `FeaturedShows` sorts the shows by id and then calls `random.Random(seed).sample(...)`, so the same seed and the same downloaded data always give the same `featured_shows` list. `run_info.json` records the settings that were used, the settings file, the Python version, the platform, and the versions of tvsummary, requests, pytest, mypy and ruff.

To get exactly the same list, a classmate needs the same settings file (same seed and sample size), the same data (TVmaze page 0 is stable, but TVmaze can add or edit shows), and the pinned versions in `requirements.txt` with the Python version from `environment.yml`.

## What the tests cover

There are 69 tests in `tests/`, and none of them use the network:

- `test_models.py`: `Show` cleaning, including a missing genre list, a missing rating, malformed ratings, dates and languages (parametrized), the name fallback, and records that are rejected.
- `test_aggregations.py`: one test per aggregation class with hand-made shows, plus the featured-shows tests: the same seed gives the same list, and different seeds can give different ones.
- `test_sources.py`: `requests.get` is replaced with `monkeypatch`. Each network failure becomes a `SourceError` (checked with `pytest.raises(..., match=...)`), each bad body becomes a `ResponseShapeError`, and skipped records are logged as warnings (checked with `caplog`).
- `test_config.py`: a valid file, a missing file, broken TOML, and each kind of missing or bad setting.
- `test_report.py`: the summary keys, writing files under `tmp_path`, an unwritable path, and `run_info.json`.
- `test_main.py`: exit code 1 and the `Error:` line for a missing config and for a failed download, exit code 0 with both files written, and two runs giving the same featured shows.
- `conftest.py` holds the shared fixtures: `make_raw`, `sample_shows`, `settings` and `settings_file`.

I chose not to test the real TVmaze API. A test that calls it would fail without Wi-Fi or whenever TVmaze changes its data, so the download is tested with fake responses instead.

## Comparing with Lab 03

`data/reference/lab02_summary.json` is the output from the real Lab 02 run, which Lab 03 reproduced exactly. Compared with the new `data/processed/summary.json`, every key and value is the same apart from `generated_at`, and the only new key is `featured_shows`.

## Known limitations

The program only downloads the first page of shows, not the whole TVmaze catalogue. The output folder is relative, so the program must be run from the repository root. The featured shows only repeat if TVmaze returns the same shows. The average rating for a language with very few rated shows is not very reliable.
