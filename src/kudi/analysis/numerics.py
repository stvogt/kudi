"""Numeric utilities for IRC analyses."""

from __future__ import annotations

from typing import Iterable, List

from ..models import IrcPoint

HARTREE_TO_KCAL_MOL = 627.509474


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
