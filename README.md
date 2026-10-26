# TV Show Summary (tvsummary)

This package downloads a page of TV shows from the free TVmaze API and turns it into a short JSON report: shows per genre, average rating per language, shows per decade, the top-rated shows, and how much information is missing. It is my Lab 02 program restructured as an installable package; it gives the same summary for the same data.

## Data source

https://api.tvmaze.com/shows?page=0. Each record is one TV show, with its name, language, genres, premiere date, rating, and the network or streaming service where it airs. The page returns about 240 shows. No account or API key is needed.

## Setup

    conda env create -f environment.yml
    conda activate tvsummary
    pip install -r requirements.txt
    pip install -e .

## Run

    python main.py

The report is written to `data/processed/summary.json`. With no internet connection the program prints a one-line message such as `Download failed: could not connect to the server. Check your internet connection.` and stops, without a traceback.

The Lab 02 output is kept in `data/reference/lab02_summary.json` so the two can be compared. Only `generated_at` should differ.

## Test

    python -m unittest discover -s tests

The tests use handmade records only and need no network.

## Layout

- `main.py`: the entry point. It only connects the pieces and prints messages, so the package can be reused without it.
- `src/tvsummary/config.py`: the source URL, timeout, output path and top-rated limit, so a setting is changed in one place.
- `src/tvsummary/models.py`: the `Show` record class. All the checks for missing or malformed fields live here.
- `src/tvsummary/sources.py`: `TVMazeSource`, which downloads the records and turns them into `Show` objects. It is the only module that imports `requests`, so changing the data source touches only this file.
- `src/tvsummary/aggregations.py`: the `Aggregation` base class and one subclass per section of the report.
- `src/tvsummary/report.py`: builds the summary dict and writes it as JSON. Separate so the output format can change without touching the calculations.
- `src/tvsummary/__init__.py`: re-exports the public names, so you can write `from tvsummary import Show`.
- `tests/`: unit tests for the record class, the parsing step and the aggregations.

## What moved where

| Lab 02 (`records.py`) | Lab 03 |
|---|---|
| `SOURCE_URL`, `TIMEOUT_SECONDS`, `OUTPUT` | `config.py`: `SOURCE_URL`, `TIMEOUT_SECONDS`, `OUTPUT_PATH` (now `data/processed/summary.json`) |
| `DownloadError` | `sources.py`: `DownloadError` |
| `fetch_records()` | `sources.py`: `TVMazeSource.fetch_raw()` |
| `clean_records()` | `sources.py`: `TVMazeSource.parse()` (the per-record checks moved into `Show.__init__`) |
| `get_genres()` | `models.py`: `Show._clean_genres()`, stored as `Show.genres` |
| `get_rating()` | `models.py`: `Show._clean_rating()`, stored as `Show.rating` |
| `get_language()` | `models.py`: `Show._clean_language()`, stored as `Show.language` |
| `get_premiere_year()` | `models.py`: `Show._clean_premiere_year()`, stored as `Show.premiere_year` |
| `get_channel_kind()` | `models.py`: `Show._clean_channel_kind()`, stored as `Show.channel_kind` |
| `get_name()` | `models.py`: `Show._clean_name()`, stored as `Show.name` |
| `shows_per_genre()` | `aggregations.py`: `ShowsPerGenre.compute()` |
| `average_rating_by_language()` | `aggregations.py`: `AverageRatingByLanguage.compute()` |
| `shows_per_decade()` | `aggregations.py`: `ShowsPerDecade.compute()` |
| `top_rated_shows()` | `aggregations.py`: `TopRatedShows.compute()` (the limit is set in `__init__`) |
| `data_quality()` | `aggregations.py`: `DataQuality.compute()` |
| `build_summary()` | `report.py`: `build_summary()`, which now loops over a list of aggregation objects |
| `write_summary()` | `report.py`: `write_summary()`, which now also creates the output folder |
| `main()` | `main.py`: `main()` |

## Design choices

**Show** exists so that one TV show is cleaned once, when it is created. In Lab 02 every aggregation called the field readers again on the raw dict. Now `Show.__init__` does every check, and the rest of the program reads clean attributes (`show.rating`, `show.genres`) and never sees the raw JSON. A record that cannot be identified (not a dict, or no integer id) raises `InvalidRecordError`, which the source counts as skipped. `__str__` gives a readable line such as `Breaking Bad (2008, 9.2)`.

**TVMazeSource** exists so that downloading is one object with one job. It keeps the URL and timeout, turns every network failure into a `DownloadError` with a clear message, and returns `Show` objects instead of raw dictionaries. `parse()` is a static method so the tests can check it with handmade records and no network.

**FetchResult** is a small dataclass that carries the shows together with how many records were downloaded and skipped, because the report needs all three.

**Aggregation** is the base class for every section of the report. It provides the `key` (the section's name in the JSON) and a `compute(shows)` method that each subclass overrides. `build_summary()` loops over a list of aggregations and calls `compute()` on each one without checking which subclass it is. This is the reason inheritance is used here: the report builder does not need to change when a section is added or removed.

Adding one more aggregation means writing one subclass in `aggregations.py` with a `key` and a `compute()` method, and adding it to `default_aggregations()`. Nothing in `report.py` or `main.py` changes.

**main.py** stays thin. It catches `DownloadError` and `OSError` and exits with a message, so a failed download or a failed write never shows a traceback.

## Known limitations

The program only downloads the first page of shows, not the whole TVmaze catalogue. The average rating for a language with very few rated shows is not very reliable. Genres are used exactly as TVmaze writes them, so similar genres are not combined. The output path is relative, so the program should be run from the repository root.
