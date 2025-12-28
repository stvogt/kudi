"""Public API for the Kudi Gaussian IRC parser."""

from importlib import metadata as importlib_metadata

from .analysis.irc_path import IRCPath
from .exceptions import IncompleteJobError, ParseError, UnsupportedFormatError

try:
    __version__ = importlib_metadata.version(__package__ or __name__)
except importlib_metadata.PackageNotFoundError:  # pragma: no cover - fallback when not installed
    __version__ = "0.0.0"

__all__ = [
    "IRCPath",
    "ParseError",
    "UnsupportedFormatError",
    "IncompleteJobError",
    "__version__",
]
