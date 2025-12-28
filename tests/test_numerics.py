import pytest

from kudi.analysis.numerics import HARTREE_TO_KCAL_MOL, relative_energies
from kudi.models import IrcPoint


def test_relative_energy_min_rx_reference():
    points = [
        IrcPoint(rx_coord=-0.2, energy_hartree=-1.0),
        IrcPoint(rx_coord=0.0, energy_hartree=-0.5),
    ]
    rel = relative_energies(points, reference="min_rx")
    assert rel[0] == 0.0
    assert rel[1] == (points[1].energy_hartree - points[0].energy_hartree) * HARTREE_TO_KCAL_MOL


def test_relative_energies_from_real_file(irc_path_obj):
    rel = irc_path_obj.relative_energies_kcal(reference="min_rx")
    assert len(rel) == len(irc_path_obj.points)
    assert pytest.approx(0.0) == min(rel)
    assert all(value is not None for value in rel)
