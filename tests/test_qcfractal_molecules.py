from __future__ import annotations

from types import SimpleNamespace

import pytest

from kudi.models import Atom, Geometry, IrcPoint
from kudi.qcfractal import molecules


def test_molecule_from_geometry_uses_qcelemental(monkeypatch):
    captured = {}

    class FakeMolecule:
        @staticmethod
        def from_data(data, molecular_charge, molecular_multiplicity):
            captured["data"] = data
            captured["charge"] = molecular_charge
            captured["multiplicity"] = molecular_multiplicity
            return {"ok": True}

    monkeypatch.setattr(
        molecules,
        "_require_qcel_models",
        lambda: SimpleNamespace(Molecule=FakeMolecule),
    )

    geom = Geometry(atoms=[Atom(symbol="H", x=0.0, y=0.0, z=0.0), Atom(symbol="H", x=0.0, y=0.0, z=0.74)])
    result = molecules.molecule_from_geometry(geom, charge=0, multiplicity=1)

    assert result == {"ok": True}
    assert "H 0.0 0.0 0.0" in captured["data"]
    assert captured["charge"] == 0
    assert captured["multiplicity"] == 1


def test_molecule_from_irc_point_requires_geometry():
    point = IrcPoint(rx_coord=0.0, energy_hartree=-1.0, geometry=None)
    with pytest.raises(ValueError, match="no geometry"):
        molecules.molecule_from_irc_point(point)
