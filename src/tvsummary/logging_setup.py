"""Logging is configured once, here, and called from main().

Every other module only does logger = logging.getLogger(__name__) and
logs; none of them decide where messages go or how they look.
"""

import logging
import sys

_HANDLER_NAME = "tvsummary-console"
_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"


def configure_logging(level: str = "INFO") -> None:
    """Send log messages at `level` and above to standard error.

    Safe to call more than once: the handler added by an earlier call is
    replaced, so messages are never printed twice.
    """
    root = logging.getLogger()
    for handler in list(root.handlers):
        if handler.get_name() == _HANDLER_NAME:
            root.removeHandler(handler)

    handler = logging.StreamHandler(sys.stderr)
    handler.set_name(_HANDLER_NAME)
    handler.setFormatter(logging.Formatter(_FORMAT, datefmt="%H:%M:%S"))
    root.addHandler(handler)
    root.setLevel(level.upper())
