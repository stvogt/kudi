"""Single-point submission and status helpers for QCFractal."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable

TAG_PATTERN = re.compile(r"^cm\.[a-z0-9._-]+\.[a-z0-9._-]+\.[a-z0-9._-]+$")


@dataclass
class SinglepointSubmitResult:
    """Metadata returned from a single-point submission."""

    inserted: list[int]
    existing: list[int]
    errors: list[int]
    record_ids: list[int]


@dataclass
class SinglepointStatus:
    """Thin status payload for one single-point record."""

    record_id: int
    status: str
    manager_name: str | None
    modified_on: str | None


def validate_compute_tag(tag: str) -> str:
    """Validate tags against `cm.<agent>.<purpose>.<env>` conventions."""

    if not TAG_PATTERN.fullmatch(tag):
        raise ValueError(
            "Invalid compute tag. Expected format `cm.<agent>.<purpose>.<env>` "
            "using lowercase [a-z0-9._-]."
        )
    return tag


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def submit_singlepoints(
    client: Any,
    *,
    molecules: Iterable[Any],
    program: str,
    method: str,
    basis: str | None,
    tag: str,
    driver: str = "energy",
    priority: str = "normal",
    find_existing: bool = True,
) -> SinglepointSubmitResult:
    """Submit one or more single-point calculations."""

    validate_compute_tag(tag)

    meta, record_ids = client.add_singlepoints(
        molecules=list(molecules),
        program=program,
        driver=driver,
        method=method,
        basis=basis,
        compute_tag=tag,
        compute_priority=priority,
        find_existing=find_existing,
    )
    return SinglepointSubmitResult(
        inserted=_as_list(getattr(meta, "inserted_idx", [])),
        existing=_as_list(getattr(meta, "existing_idx", [])),
        errors=_as_list(getattr(meta, "error_idx", [])),
        record_ids=_as_list(record_ids),
    )


def submit_singlepoint(
    client: Any,
    *,
    molecule: Any,
    program: str,
    method: str,
    basis: str | None,
    tag: str,
    driver: str = "energy",
    priority: str = "normal",
    find_existing: bool = True,
) -> SinglepointSubmitResult:
    """Submit one single-point calculation."""

    return submit_singlepoints(
        client,
        molecules=[molecule],
        program=program,
        method=method,
        basis=basis,
        tag=tag,
        driver=driver,
        priority=priority,
        find_existing=find_existing,
    )


def get_singlepoint_status(client: Any, record_ids: Iterable[int]) -> list[SinglepointStatus]:
    """Fetch basic status information for single-point records."""

    record_ids_list = list(record_ids)
    records = client.get_singlepoints(record_ids_list, missing_ok=True)
    records_list = _as_list(records)

    output: list[SinglepointStatus] = []
    for requested_id, record in zip(record_ids_list, records_list):
        if record is None:
            output.append(
                SinglepointStatus(
                    record_id=requested_id,
                    status="missing",
                    manager_name=None,
                    modified_on=None,
                )
            )
            continue

        output.append(
            SinglepointStatus(
                record_id=getattr(record, "id", requested_id),
                status=str(getattr(record, "status", "unknown")),
                manager_name=getattr(record, "manager_name", None),
                modified_on=str(getattr(record, "modified_on", None))
                if getattr(record, "modified_on", None) is not None
                else None,
            )
        )
    return output


def format_singlepoint_status(status: SinglepointStatus) -> str:
    """Render a stable human-readable status line."""

    return (
        f"id={status.record_id} status={status.status} "
        f"manager={status.manager_name} modified_on={status.modified_on}"
    )
