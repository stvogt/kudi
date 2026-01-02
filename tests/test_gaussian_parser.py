import pytest

from kudi.parsing.gaussian import parse_gaussian_block


def test_gaussian_energy_extraction(irc_blocks):
    point = parse_gaussian_block(irc_blocks[0])
    assert isinstance(point.rx_coord, float)
    assert isinstance(point.energy_hartree, float)


def test_orbital_concatenation_collects_multi_line(irc_blocks):
    point = parse_gaussian_block(irc_blocks[1], strict=False)
    if point.occ_orbitals is not None:
        assert all(isinstance(value, float) for value in point.occ_orbitals)
        assert len(point.occ_orbitals) > 0
    if point.virt_orbitals is not None:
        assert all(isinstance(value, float) for value in point.virt_orbitals)
        assert len(point.virt_orbitals) > 0


def _extract_first_atom_from_last_orientation(block):
    indices = [i for i, line in enumerate(block) if "Standard orientation" in line or "Input orientation" in line]
    last_start = indices[-1]
    dash_indices = [i for i in range(last_start, len(block)) if block[i].strip() and set(block[i].strip()) == {"-"}]
    table_start = dash_indices[1] + 1
    parts = block[table_start].split()
    return tuple(map(float, parts[3:6]))


def test_geometry_uses_last_standard_orientation(irc_blocks):
    block = irc_blocks[0]
    expected_coords = _extract_first_atom_from_last_orientation(block)
    point = parse_gaussian_block(block)
    assert point.geometry is not None
    assert len(point.geometry.atoms) > 0
    first_atom = point.geometry.atoms[0]
    assert (first_atom.x, first_atom.y, first_atom.z) == pytest.approx(expected_coords)


def test_non_strict_allows_missing_data():
    empty_block = ["Random text"]
    point = parse_gaussian_block(empty_block, strict=False)
    assert point.rx_coord is None
    assert point.energy_hartree is None


def test_energy_prefers_last_occurrence():
    block = [
        " Single Point computation for reaction coordinate:   0.0000",
        " SCF Done:  E(RB3LYP) =   -100.100100",
        " Random iteration data",
        " SCF Done:  E(RB3LYP) =   -100.200200",
    ]

    point = parse_gaussian_block(block)

    assert point.energy_hartree == pytest.approx(-100.2002)
