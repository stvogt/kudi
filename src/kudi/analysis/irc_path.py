"""High-level interface for Gaussian IRC data."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Optional

from ..exceptions import ParseError
from ..io import read_lines
from ..models import IrcPoint, NboBondOrbital
from ..parsing.gaussian import parse_gaussian_block
from ..parsing.irc import segment_irc_blocks
from ..parsing.nbo import parse_bond_orbitals, parse_natural_charges, parse_wiberg_indices
from .numerics import relative_energies


class IRCPath:
    def __init__(self, path: Path, points: List[IrcPoint]):
        self.path = path
        self.points = points

    @classmethod
    def from_file(cls, path: Path | str, *, strict: bool = False) -> "IRCPath":
        file_path = Path(path)
        lines = read_lines(file_path)
        blocks = segment_irc_blocks(lines, strict=strict)

        points: List[IrcPoint] = []
        for block in blocks:
            try:
                point = parse_gaussian_block(block, strict=strict)
            except ParseError:
                if strict:
                    raise
                point = parse_gaussian_block(block, strict=False)

            if not strict and (point.rx_coord is None or point.energy_hartree is None):
                continue
            charges = parse_natural_charges(block)
            wiberg = parse_wiberg_indices(block)
            bond_orbs = parse_bond_orbitals(block)

            if charges:
                point.nbo_charges = charges
            if wiberg:
                point.wiberg_bonds = wiberg
            if bond_orbs:
                point.bond_orbitals = bond_orbs
            points.append(point)

        if strict and not points:
            raise ParseError("No IRC points parsed from file")

        return cls(file_path, points)

    @property
    def rx_coords(self) -> List[Optional[float]]:
        return [point.rx_coord for point in self.points]

    @property
    def energies_hartree(self) -> List[Optional[float]]:
        return [point.energy_hartree for point in self.points]

    @property
    def occ_orbitals(self) -> List[Optional[List[float]]]:
        return [point.occ_orbitals for point in self.points]

    @property
    def virt_orbitals(self) -> List[Optional[List[float]]]:
        return [point.virt_orbitals for point in self.points]

    @property
    def geometries(self):
        return [point.geometry for point in self.points]

    def relative_energies_kcal(self, *, reference: str = "min_rx") -> List[float]:
        return relative_energies(self.points, reference=reference)

    def nbo_charges(self, atom_labels: Optional[Iterable[str]] = None) -> Dict[str, List[Optional[float]]]:
        labels = set(atom_labels) if atom_labels is not None else set()
        for point in self.points:
            if point.nbo_charges:
                labels.update(point.nbo_charges.keys())
        charges: Dict[str, List[Optional[float]]] = {label: [] for label in labels}

        for point in self.points:
            for label in labels:
                value = point.nbo_charges.get(label) if point.nbo_charges else None
                charges[label].append(value)
        return charges

    def wiberg_bond_orders(self, bonds: Optional[Iterable[str]] = None) -> Dict[str, List[Optional[float]]]:
        bond_keys = set(bonds) if bonds is not None else set()
        for point in self.points:
            if point.wiberg_bonds:
                bond_keys.update(point.wiberg_bonds.keys())
        bond_series: Dict[str, List[Optional[float]]] = {bond: [] for bond in bond_keys}

        for point in self.points:
            for bond in bond_keys:
                value = point.wiberg_bonds.get(bond) if point.wiberg_bonds else None
                bond_series[bond].append(value)
        return bond_series

    def bond_orbitals(self, keys: Optional[Iterable[str]] = None) -> Dict[str, List[Optional[NboBondOrbital]]]:
        orbital_keys = set(keys) if keys is not None else set()
        for point in self.points:
            if point.bond_orbitals:
                orbital_keys.update(point.bond_orbitals.keys())
        orbital_series: Dict[str, List[Optional[NboBondOrbital]]] = {key: [] for key in orbital_keys}

        for point in self.points:
            for key in orbital_keys:
                value = point.bond_orbitals.get(key) if point.bond_orbitals else None
                orbital_series[key].append(value)
        return orbital_series


ReactionPath = IRCPath
