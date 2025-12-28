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
