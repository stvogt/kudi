"""Portal client helpers with optional QCFractal dependencies."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

DEFAULT_CONNECTION = Path(
    os.environ.get("KUDI_QCFRACTAL_CONNECTION", "/home/zuse/qcfractal/connection.yaml")
)


def _require_yaml() -> Any:
    try:
        import yaml
    except ModuleNotFoundError as exc:
        raise ImportError(
            "PyYAML is required for QCFractal connection files. "
            "Install with: pip install 'kudi[qcfractal]'"
        ) from exc
    return yaml


def _require_portal_client() -> Any:
    try:
        from qcportal import PortalClient
    except ModuleNotFoundError as exc:
        raise ImportError(
            "qcportal is required for QCFractal integration. "
            "Install with: pip install 'kudi[qcfractal]'"
        ) from exc
    return PortalClient


def load_connection(path: Path | str = DEFAULT_CONNECTION) -> dict[str, Any]:
    """Load QCFractal connection settings from a YAML file."""

    yaml = _require_yaml()
    connection_path = Path(path)
    with connection_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def make_client(
    connection_path: Path | str = DEFAULT_CONNECTION,
    *,
    api_url: str | None = None,
    username: str | None = None,
    password: str | None = None,
    verify_tls: bool | None = None,
):
    """Construct a PortalClient from connection file defaults and overrides."""

    cfg = load_connection(connection_path)
    server_cfg = cfg.get("server", {})
    auth_cfg = cfg.get("manager_auth", {})

    url = api_url or server_cfg.get("api_url")
    if not url:
        raise ValueError("Missing API URL; provide --api-url or include server.api_url in connection config")

    user = username if username is not None else auth_cfg.get("username")
    pwd = password if password is not None else auth_cfg.get("password")

    if verify_tls is None:
        verify = auth_cfg.get("verify_tls", True)
    else:
        verify = verify_tls

    PortalClient = _require_portal_client()
    return PortalClient(url, username=user, password=pwd, verify=verify, show_motd=False)
