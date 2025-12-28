"""Parsers for NBO output sections."""

from __future__ import annotations

import re
from typing import Dict, List

from ..models import NboBondOrbital


def parse_natural_charges(block: List[str]) -> Dict[str, float]:
    charges: Dict[str, float] = {}
    try:
        start = next(i for i, line in enumerate(block) if "Summary of Natural Population Analysis:" in line)
    except StopIteration:
        return charges

    for line in block[start + 1 :]:
        if not line.strip():
            break
        parts = line.split()
        if len(parts) < 3 or not parts[0].isdigit():
            continue
        index = parts[0]
        symbol = parts[1]
        try:
            value = float(parts[2])
        except ValueError:
            continue
        label = f"{symbol}{index}"
        charges[label] = value
    return charges


def parse_wiberg_indices(block: List[str]) -> Dict[str, float]:
    bonds: Dict[str, float] = {}
    try:
        start = next(i for i, line in enumerate(block) if "Wiberg bond index matrix in the NAO basis:" in line)
    except StopIteration:
        return bonds

    idx = start + 1
    while idx < len(block) and not block[idx].strip():
        idx += 1
    if idx >= len(block):
        return bonds

    column_header = block[idx].split()
    data_lines: List[str] = []
    for line in block[idx + 1 :]:
        if not line.strip():
            break
        data_lines.append(line)

    if not data_lines:
        return bonds

    row_map: Dict[str, str] = {}
    for line in data_lines:
        parts = line.split()
        if len(parts) >= 2 and parts[0].isdigit():
            row_map[parts[0]] = parts[1]

    for line in data_lines:
        parts = line.split()
        if len(parts) < 3:
            continue
        row_index = parts[0]
        row_label = row_map.get(row_index, parts[1])
        values = parts[2:]
        for col_idx, raw in enumerate(values):
            if col_idx >= len(column_header):
                continue
            col_index = column_header[col_idx]
            col_label = row_map.get(col_index, col_index)
            if raw in {"-", "--"} or col_label == row_label:
                continue
            try:
                value = float(raw)
            except ValueError:
                continue
            key = "-".join(sorted([row_label, col_label]))
            bonds[key] = value
    return bonds


def parse_bond_orbitals(block: List[str]) -> Dict[str, NboBondOrbital]:
    orbitals: Dict[str, NboBondOrbital] = {}
    try:
        start = next(i for i, line in enumerate(block) if "Bond orbital/ Coefficients/ Hybrids" in line)
    except StopIteration:
        return orbitals

    orbital_pattern = re.compile(
        r"\s*\d+\.\s*(BD\*?|LP)\s*\(\s*\d+\)\s*([A-Za-z]+)\s*(\d+)(?:\s*-\s*([A-Za-z]+)\s*(\d+))?\s+([0-9]+\.\d+)"
    )

    for line in block[start + 1 :]:
        if not line.strip():
            if orbitals:
                break
            continue
        match = orbital_pattern.match(line)
        if not match:
            continue
        kind, atom1, idx1, atom2, idx2, occ = match.groups()
        contributors = [f"{atom1}{idx1}"]
        if atom2 and idx2:
            contributors.append(f"{atom2}{idx2}")
        key = "-".join(contributors)
        orbital = NboBondOrbital(
            kind=kind,
            occupancy=float(occ),
            key=key,
            contributors=contributors,
        )
        orbitals[key] = orbital
    return orbitals
