"""Parse Gaussian IRC blocks."""

from __future__ import annotations

import re
from typing import List, Optional

from ..exceptions import ParseError
from ..models import Atom, Geometry, IrcPoint
from .irc import ANCHOR, extract_rx_from_anchor_line

ATOMIC_SYMBOLS = {
    1: "H",
    2: "He",
    3: "Li",
    4: "Be",
    5: "B",
    6: "C",
    7: "N",
    8: "O",
    9: "F",
    10: "Ne",
    11: "Na",
    12: "Mg",
    13: "Al",
    14: "Si",
    15: "P",
    16: "S",
    17: "Cl",
    18: "Ar",
    19: "K",
    20: "Ca",
    21: "Sc",
    22: "Ti",
    23: "V",
    24: "Cr",
    25: "Mn",
    26: "Fe",
    27: "Co",
    28: "Ni",
    29: "Cu",
    30: "Zn",
    31: "Ga",
    32: "Ge",
    33: "As",
    34: "Se",
    35: "Br",
    36: "Kr",
}


def parse_gaussian_block(block: List[str], *, strict: bool = True) -> IrcPoint:
    rx_coord = _find_reaction_coordinate(block)
    energy = _find_energy(block)
    occ = _collect_orbitals(block, marker="occ. eigenvalues --")
    virt = _collect_orbitals(block, marker="virt. eigenvalues --")
    geometry = _parse_geometry(block)

    if strict and (rx_coord is None or energy is None):
        raise ParseError("Missing required IRC information in Gaussian block")

    return IrcPoint(
        rx_coord=rx_coord,
        energy_hartree=energy,
        occ_orbitals=occ or None,
        virt_orbitals=virt or None,
        geometry=geometry,
    )


def _find_reaction_coordinate(block: List[str]) -> Optional[float]:
    for line in block:
        if ANCHOR in line:
            try:
                return extract_rx_from_anchor_line(line)
            except ParseError:
                continue
    return None


def _find_energy(block: List[str]) -> Optional[float]:
    energy_pattern = re.compile(r"SCF Done:\s+E\(.+?\)\s*=\s*(-?\d+\.\d+)")
    for line in block:
        match = energy_pattern.search(line)
        if match:
            return float(match.group(1))
    return None


def _collect_orbitals(block: List[str], marker: str) -> List[float]:
    values: List[float] = []
    collecting = False
    for line in block:
        if marker in line:
            collecting = True
            fragment = line.split("--", maxsplit=1)[-1]
            values.extend(_parse_float_tokens(fragment))
            continue
        if collecting and line.strip() and not any(keyword in line for keyword in ["occ. eigenvalues", "virt. eigenvalues"]):
            potential = _parse_float_tokens(line)
            if potential:
                values.extend(potential)
            else:
                collecting = False
    return values


def _parse_float_tokens(text: str) -> List[float]:
    floats: List[float] = []
    for token in text.strip().split():
        try:
            floats.append(float(token))
        except ValueError:
            continue
    return floats


def _parse_geometry(block: List[str]) -> Optional[Geometry]:
    orientation_indices: List[int] = []
    for idx, line in enumerate(block):
        if "Standard orientation" in line or "Input orientation" in line:
            orientation_indices.append(idx)
    if not orientation_indices:
        return None

    start_idx = orientation_indices[-1]
    dash_indices: List[int] = []
    for idx in range(start_idx, len(block)):
        stripped = block[idx].strip()
        if stripped and set(stripped) == {"-"}:
            dash_indices.append(idx)
    if len(dash_indices) < 3:
        return None

    table_start = dash_indices[1] + 1
    table_end = dash_indices[2]
    atom_lines = block[table_start:table_end]

    atoms: List[Atom] = []
    for line in atom_lines:
        parts = line.split()
        if len(parts) < 6:
            continue
        try:
            atomic_number = int(parts[1])
            x, y, z = map(float, parts[3:6])
        except ValueError:
            continue
        symbol = ATOMIC_SYMBOLS.get(atomic_number)
        if symbol is None:
            continue
        atoms.append(Atom(symbol=symbol, x=x, y=y, z=z))

    if not atoms:
        return None
    return Geometry(atoms=atoms)
