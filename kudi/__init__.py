"""Kudi package public API."""

__version__ = '0.3.0'
__author__ = "Stefan Vogt <stvogtgeisse@qcmmlab.com>"

__all__ = ['Path']


def __getattr__(name):
    if name == 'Path':
        from .kudi import Path
        return Path
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
