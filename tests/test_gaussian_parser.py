import pytest
from pathlib import Path

from kudi.parsing.gaussian import parse_gaussian_block
from kudi.parsing.irc import segment_irc_blocks
from kudi.io import read_lines


def _first_block():
    lines = read_lines(Path("tests/fixtures/gaussian_irc.log"))
    return segment_irc_blocks(lines)[0]


def _second_block():
    lines = read_lines(Path("tests/fixtures/gaussian_irc.log"))
    return segment_irc_blocks(lines)[1]


def test_gaussian_energy_extraction():
    point = parse_gaussian_block(_first_block())
    assert point.energy_hartree == pytest.approx(-150.12345678)


def test_orbital_concatenation_collects_multi_line():
    point = parse_gaussian_block(_second_block())
    assert point.occ_orbitals[-1] == pytest.approx(-0.5)
    assert point.virt_orbitals == pytest.approx([0.6, 0.9])


def test_geometry_uses_last_standard_orientation():
    point = parse_gaussian_block(_first_block())
    assert point.geometry is not None
    assert len(point.geometry.atoms) == 2
    assert point.geometry.atoms[0].symbol == "C"


def test_non_strict_allows_missing_data():
    empty_block = ["Random text"]
    point = parse_gaussian_block(empty_block, strict=False)
    assert point.rx_coord is None
    assert point.energy_hartree is None
