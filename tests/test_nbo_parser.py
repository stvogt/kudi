from pathlib import Path

from kudi.parsing.nbo import parse_bond_orbitals, parse_natural_charges, parse_wiberg_indices
from kudi.parsing.irc import segment_irc_blocks
from kudi.io import read_lines


def _first_block():
    lines = read_lines(Path("tests/fixtures/gaussian_irc.log"))
    return segment_irc_blocks(lines)[0]


def test_natural_charges_extract_label():
    charges = parse_natural_charges(_first_block())
    assert charges["C1"] == -0.12345


def test_wiberg_indices_reconstruct_bond():
    wiberg = parse_wiberg_indices(_first_block())
    assert wiberg["C1-H2"] == 0.90


def test_bond_orbital_entries_parsed():
    orbitals = parse_bond_orbitals(_first_block())
    assert "C1-C2" in orbitals
    assert orbitals["C1-C2"].kind == "BD"
