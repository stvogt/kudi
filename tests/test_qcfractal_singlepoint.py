from __future__ import annotations

from types import SimpleNamespace

import pytest

from kudi.qcfractal.singlepoint import (
    format_singlepoint_status,
    get_singlepoint_status,
    submit_singlepoint,
    validate_compute_tag,
)


class DummyClient:
    def __init__(self):
        self.submit_kwargs = None

    def add_singlepoints(self, **kwargs):
        self.submit_kwargs = kwargs
        meta = SimpleNamespace(inserted_idx=[0], existing_idx=[], error_idx=[])
        return meta, [1234]

    def get_singlepoints(self, record_ids, missing_ok):
        assert missing_ok is True
        assert record_ids == [1234, 9999]
        return [
            SimpleNamespace(id=1234, status="complete", manager_name="cm.test", modified_on="2026-02-21"),
            None,
        ]


def test_validate_compute_tag_accepts_expected_format():
    assert validate_compute_tag("cm.agent.sp.prod") == "cm.agent.sp.prod"


def test_validate_compute_tag_rejects_invalid_format():
    with pytest.raises(ValueError):
        validate_compute_tag("agent.sp.prod")


def test_submit_singlepoint_passes_expected_payload():
    client = DummyClient()
    result = submit_singlepoint(
        client,
        molecule={"symbols": ["H", "H"]},
        program="psi4",
        method="b3lyp",
        basis="def2-svp",
        tag="cm.agent.sp.prod",
        driver="energy",
        priority="normal",
    )

    assert result.record_ids == [1234]
    assert client.submit_kwargs is not None
    assert client.submit_kwargs["compute_tag"] == "cm.agent.sp.prod"
    assert client.submit_kwargs["program"] == "psi4"
    assert client.submit_kwargs["method"] == "b3lyp"
    assert client.submit_kwargs["basis"] == "def2-svp"


def test_get_singlepoint_status_formats_missing_and_present():
    client = DummyClient()
    statuses = get_singlepoint_status(client, [1234, 9999])
    assert [status.status for status in statuses] == ["complete", "missing"]
    assert format_singlepoint_status(statuses[0]) == (
        "id=1234 status=complete manager=cm.test modified_on=2026-02-21"
    )
