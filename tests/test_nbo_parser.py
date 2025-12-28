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
