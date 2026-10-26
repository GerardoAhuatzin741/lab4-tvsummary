"""All the settings the program uses, kept in one place.

Paths are relative to the folder you run the program from (the
repository root), so nothing here depends on one person's computer.
"""

from pathlib import Path

# Where the shows come from: the first page of the TVmaze show index.
SOURCE_URL = "https://api.tvmaze.com/shows?page=0"

# How many seconds to wait for the server before giving up.
TIMEOUT_SECONDS = 10

# Where the summary is written.
OUTPUT_PATH = Path("data") / "processed" / "summary.json"

# How many shows the top-rated list keeps.
TOP_RATED_LIMIT = 10
