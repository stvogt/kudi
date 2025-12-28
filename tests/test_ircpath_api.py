from pathlib import Path

from kudi import IRCPath


def test_from_file_builds_points():
    irc = IRCPath.from_file(Path("tests/fixtures/gaussian_irc.log"))
    assert len(irc.points) == 2
    assert irc.rx_coords[0] == -0.1


def test_accessors_are_aligned():
    irc = IRCPath.from_file(Path("tests/fixtures/gaussian_irc.log"))
    assert len(irc.occ_orbitals) == len(irc.points)
    assert len(irc.virt_orbitals) == len(irc.points)
    assert len(irc.geometries) == len(irc.points)


def test_relative_energies_first_reference():
    irc = IRCPath.from_file(Path("tests/fixtures/gaussian_irc.log"))
    rel = irc.relative_energies_kcal(reference="first")
    assert rel[0] == 0.0
    assert rel[1] > 0


def test_nbo_accessors_align():
    irc = IRCPath.from_file(Path("tests/fixtures/gaussian_irc.log"))
    charges = irc.nbo_charges()
    assert set(charges.keys()) == {"C1", "H2", "O1", "H3"}
    assert all(len(values) == len(irc.points) for values in charges.values())

    wiberg = irc.wiberg_bond_orders()
    assert "C1-H2" in wiberg and "H2-O1" in wiberg
    assert all(len(values) == len(irc.points) for values in wiberg.values())

    bond_orbitals = irc.bond_orbitals()
    assert "C1-C2" in bond_orbitals
    assert bond_orbitals["C1-C2"][0] is not None
