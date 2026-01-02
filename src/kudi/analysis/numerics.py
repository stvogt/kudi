"""Numeric utilities for IRC analyses."""

from __future__ import annotations

from typing import Iterable, List, Sequence

try:
    import numpy as np
except ModuleNotFoundError as exc:
    raise ImportError("NumPy is required for numeric analyses. Please install numpy.") from exc

from ..models import IrcPoint

HARTREE_TO_KCAL_MOL = 627.509474


def differentiate(x: Sequence[float], y: Sequence[float]) -> np.ndarray:
    """Return ``dy/dx`` using :func:`numpy.gradient`.

    Parameters
    ----------
    x, y:
        One-dimensional sequences of equal length. ``x`` must be monotonic
        (non-decreasing or non-increasing). ``len(x)`` must be at least 3.

    Returns
    -------
    numpy.ndarray
        Derivative values aligned with the input coordinates.
    """

    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)

    if x_arr.shape != y_arr.shape:
        raise ValueError("x and y must have the same shape for differentiation")
    if x_arr.ndim != 1:
        raise ValueError("x and y must be one-dimensional")
    if x_arr.size < 3:
        raise ValueError("Differentiation requires at least three points")

    diffs = np.diff(x_arr)
    monotonic_increasing = np.all(diffs >= 0)
    monotonic_decreasing = np.all(diffs <= 0)
    if not (monotonic_increasing or monotonic_decreasing):
        raise ValueError("x must be monotonic for differentiation")

    return np.gradient(y_arr, x_arr)


def relative_energies(points: Iterable[IrcPoint], *, reference: str = "min_rx") -> List[float]:
    point_list = list(points)
    if not point_list:
        return []

    energies = [p.energy_hartree for p in point_list]
    if any(energy is None for energy in energies):
        raise ValueError("Missing energies for relative energy computation")

    if reference == "first":
        reference_energy = energies[0]
    elif reference == "min_rx":
        rx_coords = [p.rx_coord for p in point_list]
        if any(rx is None for rx in rx_coords):
            raise ValueError("Missing reaction coordinates for reference selection")
        min_index = min(range(len(point_list)), key=lambda i: rx_coords[i])
        reference_energy = energies[min_index]
    else:
        raise ValueError("Unknown reference option")

    return [(energy - reference_energy) * HARTREE_TO_KCAL_MOL for energy in energies]
