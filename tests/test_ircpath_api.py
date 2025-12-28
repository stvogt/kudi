import numpy as np
import pytest

from kudi import IRCPath


def test_from_file_builds_points(irc_fixture_path):
    irc = IRCPath.from_file(irc_fixture_path)
    assert len(irc.points) > 5
    assert all(isinstance(rx, float) for rx in irc.rx_coords)


def test_accessors_are_aligned(irc_path_obj):
    assert len(irc_path_obj.occ_orbitals) == len(irc_path_obj.points)
    assert len(irc_path_obj.virt_orbitals) == len(irc_path_obj.points)
    assert len(irc_path_obj.geometries) == len(irc_path_obj.points)


def test_relative_energies_first_reference(irc_path_obj):
    rel = irc_path_obj.relative_energies_kcal(reference="min_rx")
    assert len(rel) == len(irc_path_obj.points)
    assert rel[irc_path_obj.rx_coords.index(min(irc_path_obj.rx_coords))] == pytest.approx(0.0)
    assert all(isinstance(value, float) for value in rel)


def test_nbo_accessors_align(irc_blocks, irc_path_obj):
    from kudi.parsing.nbo import parse_bond_orbitals, parse_natural_charges, parse_wiberg_indices

    block_with_charges = next(
        (block for block in irc_blocks if any("Summary of Natural Population Analysis:" in line for line in block)), None
    )
    charge_labels = list(parse_natural_charges(block_with_charges or []).keys())
    charges = irc_path_obj.nbo_charges(charge_labels or None)
    assert all(len(values) == len(irc_path_obj.points) for values in charges.values())
    assert all(value is None or isinstance(value, float) for series in charges.values() for value in series)

    block_with_wiberg = next(
        (block for block in irc_blocks if any("Wiberg bond index matrix in the NAO basis:" in line for line in block)), None
    )
    wiberg_keys = list(parse_wiberg_indices(block_with_wiberg or []).keys())
    wiberg = irc_path_obj.wiberg_bond_orders(wiberg_keys or None)
    assert all(len(values) == len(irc_path_obj.points) for values in wiberg.values())
    assert all(value is None or isinstance(value, float) for series in wiberg.values() for value in series)

    block_with_orbitals = next(
        (block for block in irc_blocks if any("Bond orbital/ Coefficients/ Hybrids" in line for line in block)), None
    )
    orbital_keys = list(parse_bond_orbitals(block_with_orbitals or []).keys())
    bond_orbitals = irc_path_obj.bond_orbitals(orbital_keys or None)
    assert all(len(values) == len(irc_path_obj.points) for values in bond_orbitals.values())


def test_reaction_force_outputs_align(irc_path_obj):
    result = irc_path_obj.reaction_force()

    assert len(result["reaction_coordinate"]) == len(irc_path_obj.points)
    assert len(result["reaction_force"]) == len(irc_path_obj.points)
    assert result["reaction_force"].dtype.kind in {"f"}


def test_reaction_force_constant_outputs_align(irc_path_obj):
    result = irc_path_obj.reaction_force_constant()

    assert len(result["reaction_coordinate"]) == len(irc_path_obj.points)
    assert len(result["reaction_force_constant"]) == len(irc_path_obj.points)
    assert result["reaction_force_constant"].dtype.kind in {"f"}


def test_chemical_potential_koopmans(irc_path_obj):
    result = irc_path_obj.chemical_potential_koopmans()

    assert len(result["reaction_coordinate"]) == len(irc_path_obj.points)
    assert len(result["chemical_potential"]) == len(irc_path_obj.points)
    assert result["chemical_potential"].dtype.kind in {"f"}
    assert not np.all(np.isnan(result["chemical_potential"]))


def test_flux_outputs_align(irc_path_obj):
    result = irc_path_obj.flux()

    assert len(result["reaction_coordinate"]) == len(irc_path_obj.points)
    assert len(result["flux"]) == len(irc_path_obj.points)
    assert result["flux"].dtype.kind in {"f"}
