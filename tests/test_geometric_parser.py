import pytest

from kudi.exceptions import ParseError
from kudi.io import read_lines
from kudi.parsing.geometric import parse_geometric_irc_xyz


def test_parse_geometric_irc_xyz_extracts_energy_and_rx():
    lines = read_lines("tests/fixtures/geometric_irc.xyz")
    points = parse_geometric_irc_xyz(lines, strict=True)

    assert len(points) == 3
    assert points[0].energy_hartree == pytest.approx(-1.1)
    assert points[1].energy_hartree == pytest.approx(-1.12)
    assert points[2].energy_hartree == pytest.approx(-1.09)
    assert points[0].rx_coord == pytest.approx(0.0)
    assert points[2].rx_coord > points[1].rx_coord > points[0].rx_coord
    assert points[0].geometry is not None
    assert len(points[0].geometry.atoms) == 2


def test_parse_geometric_irc_xyz_strict_requires_energy():
    lines = [
        "2",
        "Frame without energy",
        "H 0.0 0.0 0.0",
        "H 0.0 0.0 0.7",
    ]
    with pytest.raises(ParseError, match="Missing energy"):
        parse_geometric_irc_xyz(lines, strict=True)
