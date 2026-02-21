from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_driver_module(name: str):
    script_path = PROJECT_ROOT / "driver" / "kudi_qcf.py"
    spec = importlib.util.spec_from_file_location(name, script_path)
    if spec is None or spec.loader is None:
        raise ImportError("Unable to load kudi_qcf driver")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_submit_command_uses_json_loader(monkeypatch, capsys):
    module = load_driver_module("kudi_qcf_submit")

    calls = {}

    def fake_make_client(*args, **kwargs):
        calls["client_args"] = args
        calls["client_kwargs"] = kwargs
        return object()

    def fake_molecule_from_json(path):
        calls["json_path"] = path
        return {"fake": "molecule"}

    def fake_submit_singlepoint(client, **kwargs):
        calls["submit_kwargs"] = kwargs
        return SimpleNamespace(
            inserted=[0], existing=[], errors=[], record_ids=[8888]
        )

    monkeypatch.setattr(module, "make_client", fake_make_client)
    monkeypatch.setattr(module, "molecule_from_json", fake_molecule_from_json)
    monkeypatch.setattr(module, "submit_singlepoint", fake_submit_singlepoint)

    result = module.main(
        [
            "sp",
            "submit",
            "--molecule-json",
            "mol.json",
            "--program",
            "psi4",
            "--method",
            "b3lyp",
            "--tag",
            "cm.agent.sp.prod",
        ]
    )
    captured = capsys.readouterr()

    assert result == 0
    assert "record_ids=[8888]" in captured.out
    assert calls["submit_kwargs"]["tag"] == "cm.agent.sp.prod"
    assert calls["submit_kwargs"]["program"] == "psi4"
    assert calls["json_path"] == Path("mol.json")


def test_status_command_prints_lines(monkeypatch, capsys):
    module = load_driver_module("kudi_qcf_status")

    def fake_make_client(*args, **kwargs):
        return object()

    def fake_get_singlepoint_status(client, record_ids):
        assert record_ids == [10, 20]
        return [
            SimpleNamespace(record_id=10, status="complete", manager_name="cm.a", modified_on="2026-02-21"),
            SimpleNamespace(record_id=20, status="running", manager_name="cm.a", modified_on="2026-02-21"),
        ]

    monkeypatch.setattr(module, "make_client", fake_make_client)
    monkeypatch.setattr(module, "get_singlepoint_status", fake_get_singlepoint_status)

    result = module.main(["sp", "status", "10", "20"])
    captured = capsys.readouterr()

    assert result == 0
    assert "id=10 status=complete" in captured.out
    assert "id=20 status=running" in captured.out
