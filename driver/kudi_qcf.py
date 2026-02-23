from __future__ import annotations

import argparse
from pathlib import Path

from kudi.qcfractal.client import DEFAULT_CONNECTION, make_client
from kudi.qcfractal.molecules import molecule_from_json, molecule_from_xyz
from kudi.qcfractal.singlepoint import (
    format_singlepoint_status,
    get_singlepoint_status,
    submit_singlepoint,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="QCFractal helpers for Kudi")
    subparsers = parser.add_subparsers(dest="object", required=True)

    sp_parser = subparsers.add_parser("sp", help="Single-point operations")
    sp_subparsers = sp_parser.add_subparsers(dest="action", required=True)

    submit_parser = sp_subparsers.add_parser("submit", help="Submit one single-point computation")
    input_group = submit_parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--xyz", type=Path, help="XYZ file for molecule construction")
    input_group.add_argument("--molecule-json", type=Path, help="Path to QCElemental molecule JSON")
    submit_parser.add_argument("--charge", type=int, default=0, help="Molecular charge for --xyz input")
    submit_parser.add_argument(
        "--mult", type=int, default=1, help="Molecular multiplicity for --xyz input"
    )
    submit_parser.add_argument("--program", required=True)
    submit_parser.add_argument("--driver", default="energy")
    submit_parser.add_argument("--method", required=True)
    submit_parser.add_argument("--basis", default=None)
    submit_parser.add_argument("--tag", required=True)
    submit_parser.add_argument("--priority", default="normal", choices=["low", "normal", "high"])
    submit_parser.add_argument("--connection", type=Path, default=DEFAULT_CONNECTION)
    submit_parser.add_argument("--api-url", default=None)
    submit_parser.add_argument("--username", default=None)
    submit_parser.add_argument("--password", default=None)
    verify_group = submit_parser.add_mutually_exclusive_group()
    verify_group.add_argument("--verify-tls", action="store_true", default=None)
    verify_group.add_argument("--no-verify-tls", action="store_false", dest="verify_tls", default=None)
    submit_parser.add_argument("--no-find-existing", action="store_true")
    submit_parser.set_defaults(func=run_singlepoint_submit)

    status_parser = sp_subparsers.add_parser("status", help="Check single-point status")
    status_parser.add_argument("record_ids", nargs="+", type=int)
    status_parser.add_argument("--connection", type=Path, default=DEFAULT_CONNECTION)
    status_parser.add_argument("--api-url", default=None)
    status_parser.add_argument("--username", default=None)
    status_parser.add_argument("--password", default=None)
    verify_group_status = status_parser.add_mutually_exclusive_group()
    verify_group_status.add_argument("--verify-tls", action="store_true", default=None)
    verify_group_status.add_argument(
        "--no-verify-tls", action="store_false", dest="verify_tls", default=None
    )
    status_parser.set_defaults(func=run_singlepoint_status)

    return parser


def build_client(args: argparse.Namespace):
    return make_client(
        args.connection,
        api_url=args.api_url,
        username=args.username,
        password=args.password,
        verify_tls=args.verify_tls,
    )


def run_singlepoint_submit(args: argparse.Namespace) -> int:
    client = build_client(args)
    if args.molecule_json:
        molecule = molecule_from_json(args.molecule_json)
    else:
        molecule = molecule_from_xyz(args.xyz, charge=args.charge, multiplicity=args.mult)

    result = submit_singlepoint(
        client,
        molecule=molecule,
        program=args.program,
        driver=args.driver,
        method=args.method,
        basis=args.basis,
        tag=args.tag,
        priority=args.priority,
        find_existing=not args.no_find_existing,
    )
    print(f"inserted={result.inserted} existing={result.existing} errors={result.errors}")
    print(f"record_ids={result.record_ids}")
    return 0


def run_singlepoint_status(args: argparse.Namespace) -> int:
    client = build_client(args)
    statuses = get_singlepoint_status(client, args.record_ids)
    for status in statuses:
        print(format_singlepoint_status(status))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (FileNotFoundError, ValueError, ImportError) as exc:
        print(f"error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
