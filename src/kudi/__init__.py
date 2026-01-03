"""Public API for the Kudi Gaussian IRC parser."""

from .analysis.irc_path import IRCPath
from .exceptions import IncompleteJobError, ParseError, UnsupportedFormatError

__version__ = "0.4.0"

__all__ = [
    "IRCPath",
    "ParseError",
    "UnsupportedFormatError",
    "IncompleteJobError",
    "__version__",
]
