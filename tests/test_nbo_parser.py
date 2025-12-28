import pytest

from kudi.parsing.nbo import parse_bond_orbitals, parse_natural_charges, parse_wiberg_indices


def _find_block_with_header(blocks, header):
    for block in blocks:
        if any(header in line for line in block):
            return block
    return None


def test_natural_charges_extract_label(irc_blocks):
    block = _find_block_with_header(irc_blocks, "Summary of Natural Population Analysis:")
    charges = parse_natural_charges(block or [])
    assert isinstance(charges, dict)
    if charges:
        assert all(isinstance(key, str) for key in charges)
        assert all(isinstance(value, float) for value in charges.values())


def test_wiberg_indices_reconstruct_bond(irc_blocks):
    block = _find_block_with_header(irc_blocks, "Wiberg bond index matrix in the NAO basis:")
    wiberg = parse_wiberg_indices(block or [])
    assert isinstance(wiberg, dict)
    if wiberg:
        bond, value = next(iter(wiberg.items()))
        assert isinstance(bond, str)
        assert isinstance(value, float)


def test_bond_orbital_entries_parsed(irc_blocks):
    block = _find_block_with_header(irc_blocks, "Bond orbital/ Coefficients/ Hybrids")
    orbitals = parse_bond_orbitals(block or [])
    assert isinstance(orbitals, dict)
    if orbitals:
        key, orbital = next(iter(orbitals.items()))
        assert isinstance(key, str)
        assert orbital is not None
        assert orbital.kind in {"BD", "BD*", "LP"}


def test_hsno_wiberg_and_charges(irc_blocks, irc_fixture_path):
    if "hsno" not in irc_fixture_path.name:
        pytest.skip("HSNO-specific regression")

    npa_block = _find_block_with_header(irc_blocks, "Summary of Natural Population Analysis:")
    charges = parse_natural_charges(npa_block or [])
    assert charges["S2"] == pytest.approx(0.17841, abs=1e-6)
    assert charges["N3"] == pytest.approx(-0.18710, abs=1e-6)

    wiberg_block = _find_block_with_header(irc_blocks, "Wiberg bond index matrix in the NAO basis:")
    wiberg = parse_wiberg_indices(wiberg_block or [])

    sn_key = "-".join(sorted(["S2", "N3"]))
    assert sn_key in wiberg
    assert "S-N" not in wiberg
    assert wiberg[sn_key] == pytest.approx(1.7574, rel=1e-4)
