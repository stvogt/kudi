"""Numeric utilities for IRC analyses."""

from __future__ import annotations

from typing import Iterable, List, Sequence

import numpy as np

from ..models import IrcPoint

HARTREE_TO_KCAL_MOL = 627.509474


def differentiate(x: Sequence[float], y: Sequence[float]) -> np.ndarray:
    """Return ``dy/dx`` using second-order endpoint stencils.

    Endpoint derivatives follow the second-order one-sided formulas used by
    ``numpy.gradient(..., edge_order=2)`` on uniform grids.

    Parameters
    ----------
    x, y:
        One-dimensional sequences of equal length. ``x`` must be strictly
        monotonic (strictly increasing or strictly decreasing). ``len(x)``
        must be at least 3.

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
    monotonic_increasing = np.all(diffs > 0)
    monotonic_decreasing = np.all(diffs < 0)
    if not (monotonic_increasing or monotonic_decreasing):
        raise ValueError("x must be monotonic for differentiation")

    dy = np.empty_like(x_arr, dtype=float)

    h0 = x_arr[1] - x_arr[0]
    h1 = x_arr[-1] - x_arr[-2]
    if h0 == 0 or h1 == 0:
        raise ValueError("x must have non-zero spacing at endpoints")

    # Endpoints use second-order one-sided differences to match NumPy's
    # ``gradient(..., edge_order=2)`` behavior on uniform grids.
    dy[0] = (-3 * y_arr[0] + 4 * y_arr[1] - y_arr[2]) / (2 * h0)
    dy[-1] = (3 * y_arr[-1] - 4 * y_arr[-2] + y_arr[-3]) / (2 * h1)

    for i in range(1, x_arr.size - 1):
        dy[i] = (y_arr[i + 1] - y_arr[i - 1]) / (x_arr[i + 1] - x_arr[i - 1])

    return dy


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
