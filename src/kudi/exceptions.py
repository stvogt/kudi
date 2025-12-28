"""Custom exceptions used across the Kudi package."""


class ParseError(Exception):
    """Raised when parsing fails in strict mode."""


class UnsupportedFormatError(ParseError):
    """Raised when an unsupported input format is provided."""


class IncompleteJobError(ParseError):
    """Raised when a computation did not complete successfully."""
