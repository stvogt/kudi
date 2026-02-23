"""Parsers for geomeTRIC trajectory outputs."""

from __future__ import annotations

import re
from typing import List

import numpy as np

from ..exceptions import ParseError
from ..models import Atom, Geometry, IrcPoint

ENERGY_RE = re.compile(r"Energy\s+([-+]?(?:\d+\.?\d*|\.\d+)(?:[eEdD][-+]?\d+)?)")


def _parse_float(value: str) -> float:
    return float(value.replace("D", "E").replace("d", "e"))


def _parse_xyz_frames(lines: List[str], *, strict: bool) -> list[tuple[str, Geometry]]:
    idx = 0
    frames: list[tuple[str, Geometry]] = []
    total = len(lines)

    while idx < total:
        line = lines[idx].strip()
        if not line:
            idx += 1
            continue

        try:
            natoms = int(line)
        except ValueError as exc:
            raise ParseError(f"Expected atom count at line {idx + 1}") from exc

        if natoms <= 0:
            raise ParseError(f"Invalid atom count {natoms} at line {idx + 1}")

        if idx + 1 >= total:
            raise ParseError("Missing XYZ comment line")
        comment = lines[idx + 1].strip()

        start = idx + 2
        end = start + natoms
        if end > total:
            raise ParseError("Truncated XYZ frame")

        atoms: list[Atom] = []
        for ln, atom_line in enumerate(lines[start:end], start=start + 1):
            parts = atom_line.split()
            if len(parts) < 4:
                if strict:
                    raise ParseError(f"Malformed XYZ coordinate line {ln}")
                break
            try:
                atoms.append(
                    Atom(
                        symbol=parts[0],
                        x=float(parts[1]),
                        y=float(parts[2]),
                        z=float(parts[3]),
                    )
                )
            except ValueError:
                if strict:
                    raise ParseError(f"Invalid numeric value in XYZ coordinate line {ln}")
                break

        if len(atoms) == natoms:
            frames.append((comment, Geometry(atoms=atoms, units="angstrom")))
        elif strict:
            raise ParseError(f"Failed to parse full XYZ frame ending at line {end}")

        idx = end

    if strict and not frames:
        raise ParseError("No XYZ frames parsed")
    return frames


def _extract_energy(comment: str) -> float | None:
    match = ENERGY_RE.search(comment)
    if not match:
        return None
    return _parse_float(match.group(1))


def _cumulative_rx(geometries: list[Geometry]) -> list[float]:
    rx = [0.0]
    for prev, curr in zip(geometries, geometries[1:]):
        prev_xyz = np.asarray([[a.x, a.y, a.z] for a in prev.atoms], dtype=float)
        curr_xyz = np.asarray([[a.x, a.y, a.z] for a in curr.atoms], dtype=float)
        step = float(np.linalg.norm(curr_xyz - prev_xyz))
        rx.append(rx[-1] + step)
    return rx


def parse_geometric_irc_xyz(lines: List[str], *, strict: bool = False) -> list[IrcPoint]:
    """Parse geomeTRIC ``*_irc.xyz`` trajectories into IRC points.

    The geomeTRIC optimizer writes comment lines like
    ``Iteration <n> Energy <hartree>`` for each frame. Energies are parsed from
    that comment and reaction coordinates are reconstructed as cumulative
    Cartesian displacement in Angstrom.
    """

    frames = _parse_xyz_frames(lines, strict=strict)
    geometries = [geom for _, geom in frames]
    rx_values = _cumulative_rx(geometries) if geometries else []

    points: list[IrcPoint] = []
    for (comment, geometry), rx_coord in zip(frames, rx_values):
        energy = _extract_energy(comment)
        if strict and energy is None:
            raise ParseError(f"Missing energy in XYZ comment: {comment!r}")
        if not strict and energy is None:
            continue
        points.append(
            IrcPoint(
                rx_coord=rx_coord,
                energy_hartree=energy,
                geometry=geometry,
            )
        )

    if strict and not points:
        raise ParseError("No geomeTRIC IRC points parsed from file")
    return points
