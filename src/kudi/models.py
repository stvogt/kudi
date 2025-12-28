"""Typed containers representing IRC data."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Atom:
    symbol: str
    x: float
    y: float
    z: float


@dataclass
class Geometry:
    atoms: List[Atom]
    units: str = "angstrom"


@dataclass
class NboBondOrbital:
    kind: str
    occupancy: float
    key: str
    contributors: List[str] = field(default_factory=list)


@dataclass
class IrcPoint:
    rx_coord: Optional[float]
    energy_hartree: Optional[float]
    occ_orbitals: Optional[List[float]] = None
    virt_orbitals: Optional[List[float]] = None
    geometry: Optional[Geometry] = None
    nbo_charges: Optional[Dict[str, float]] = None
    wiberg_bonds: Optional[Dict[str, float]] = None
    bond_orbitals: Optional[Dict[str, NboBondOrbital]] = None
    complete: bool = True
