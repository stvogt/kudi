"""Demonstration CLI for supported :class:`kudi.analysis.irc_path.IRCPath` features."""

from __future__ import annotations

import argparse
import csv
import json
import logging
import re
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np

from kudi.analysis.irc_path import IRCPath
from kudi.exceptions import ParseError
from kudi.models import NboBondOrbital

logger = logging.getLogger(__name__)


def parse_atom_label(value: str) -> str:
    match = re.match(r"^([A-Za-z]+)(\d+)$", value)
    if not match:
        raise argparse.ArgumentTypeError("Atom labels must look like S2 or N3")
    symbol, index = match.groups()
    return f"{symbol.capitalize()}{index}"


def parse_bond_label(value: str) -> str:
    parts = value.split("-")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("Bonds must be provided as Atom1-Atom2, e.g., S2-N3")
    atoms = [parse_atom_label(part) for part in parts]
    return "-".join(sorted(atoms))


def configure_logging(verbose: bool) -> None:
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO, format="%(levelname)s:%(name)s:%(message)s")


def write_dat(path: Path, header: str, x: Sequence[float], y: Sequence[float]) -> None:
    if len(x) != len(y):
        raise ValueError(f"Mismatched data lengths for {path.name}: {len(x)} rx vs {len(y)} values")
    lines = [header]
    for rx_val, value in zip(x, y):
        lines.append(f"{rx_val:.10g} {value:.10g}")
    content = "\n".join(lines) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def write_series_csv(path: Path, rx: Sequence[float], labels: Sequence[str], data: Mapping[str, Sequence[float | None]]) -> None:
    if any(len(data.get(label, [])) not in {0, len(rx)} for label in labels):
        raise ValueError("Series lengths must match reaction coordinates")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["rx", *labels])
        for idx, rx_val in enumerate(rx):
            row = [f"{rx_val:.10g}"]
            for label in labels:
                series = data.get(label, [])
                value = series[idx] if idx < len(series) else None
                row.append("" if value is None else f"{value:.10g}")
            writer.writerow(row)


def serialize_bond_orbital(orbital: NboBondOrbital | None) -> dict | None:
    if orbital is None:
        return None
    return {
        "kind": orbital.kind,
        "occupancy": orbital.occupancy,
        "key": orbital.key,
        "contributors": list(orbital.contributors),
    }


def load_path(path: Path) -> IRCPath:
    return IRCPath.from_file(path)


def ensure_nbo_available(points: Iterable, attribute: str) -> bool:
    return any(getattr(point, attribute) for point in points)


def command_energy(args: argparse.Namespace) -> int:
    irc_path = load_path(args.input)
    rx = np.asarray(irc_path.rx_coords, dtype=float)
    rel_energy = np.asarray(irc_path.relative_energies_kcal(reference=args.reference), dtype=float)
    write_dat(args.out, "# rx rel_energy_kcal_mol", rx, rel_energy)
    logger.info("Energy table written to %s", args.out)
    return 0


def command_force(args: argparse.Namespace) -> int:
    irc_path = load_path(args.input)
    force_data = irc_path.reaction_force()
    write_dat(args.out, "# rx reaction_force", force_data["reaction_coordinate"], force_data["reaction_force"])
    logger.info("Reaction force table written to %s", args.out)
    return 0


def command_mu(args: argparse.Namespace) -> int:
    irc_path = load_path(args.input)
    mu_data = irc_path.chemical_potential_koopmans()
    write_dat(
        args.out,
        "# rx chemical_potential_koopmans_kcal_mol",
        mu_data["reaction_coordinate"],
        mu_data["chemical_potential"],
    )
    logger.info("Chemical potential table written to %s", args.out)
    return 0


def command_nbo_charges(args: argparse.Namespace) -> int:
    irc_path = load_path(args.input)
    if not ensure_nbo_available(irc_path.points, "nbo_charges"):
        message = "No NBO charge data found in input file"
        if args.strict:
            raise RuntimeError(message)
        logger.warning("%s; writing header only", message)
        write_series_csv(args.out, [], args.atoms, {label: [] for label in args.atoms})
        return 0

    charges = irc_path.nbo_charges(atom_labels=args.atoms)
    rx = np.asarray(irc_path.rx_coords, dtype=float)
    write_series_csv(args.out, rx, args.atoms, charges)
    logger.info("NBO charges written to %s", args.out)
    return 0


def command_wiberg(args: argparse.Namespace) -> int:
    irc_path = load_path(args.input)
    if not ensure_nbo_available(irc_path.points, "wiberg_bonds"):
        message = "No Wiberg bond index data found in input file"
        if args.strict:
            raise RuntimeError(message)
        logger.warning("%s; writing header only", message)
        write_series_csv(args.out, [], args.bonds, {bond: [] for bond in args.bonds})
        return 0

    bond_orders = irc_path.wiberg_bond_orders(bonds=args.bonds)
    rx = np.asarray(irc_path.rx_coords, dtype=float)
    write_series_csv(args.out, rx, args.bonds, bond_orders)
    logger.info("Wiberg bond orders written to %s", args.out)
    return 0


def command_bond_orbitals(args: argparse.Namespace) -> int:
    irc_path = load_path(args.input)
    if not ensure_nbo_available(irc_path.points, "bond_orbitals"):
        message = "No bond orbital data found in input file"
        if args.strict:
            raise RuntimeError(message)
        logger.warning("%s; writing empty JSON payload", message)
        payload = {"rx": [], "bond_orbitals": {key: [] for key in args.keys}}
    else:
        rx = list(np.asarray(irc_path.rx_coords, dtype=float))
        series = irc_path.bond_orbitals(keys=args.keys)
        payload = {
            "rx": rx,
            "bond_orbitals": {key: [serialize_bond_orbital(item) for item in series.get(key, [])] for key in args.keys},
        }

    out_path = args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2))
    logger.info("Bond orbital data written to %s", out_path)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Demonstrate IRCPath analyses via subcommands.")
    parser.add_argument("--verbose", action="store_true", help="Increase log verbosity.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    energy_parser = subparsers.add_parser("energy", help="Compute relative energies (kcal/mol).")
    energy_parser.add_argument("--input", required=True, type=Path, help="Input IRC file.")
    energy_parser.add_argument("--out", required=True, type=Path, help="Output .dat file path.")
    energy_parser.add_argument(
        "--reference",
        choices=["min_rx", "first"],
        default="min_rx",
        help="Reference point for relative energies (default: min_rx).",
    )
    energy_parser.set_defaults(func=command_energy)

    force_parser = subparsers.add_parser("force", help="Compute reaction force profile.")
    force_parser.add_argument("--input", required=True, type=Path, help="Input IRC file.")
    force_parser.add_argument("--out", required=True, type=Path, help="Output .dat file path.")
    force_parser.set_defaults(func=command_force)

    mu_parser = subparsers.add_parser("mu-koopmans", help="Compute Koopmans chemical potential profile.")
    mu_parser.add_argument("--input", required=True, type=Path, help="Input IRC file.")
    mu_parser.add_argument("--out", required=True, type=Path, help="Output .dat file path.")
    mu_parser.set_defaults(func=command_mu)

    charges_parser = subparsers.add_parser(
        "nbo-charges",
        help="Extract NBO atomic charges; without --strict writes header-only when data are missing.",
    )
    charges_parser.add_argument("--input", required=True, type=Path, help="Input IRC file.")
    charges_parser.add_argument("--atoms", nargs="+", type=parse_atom_label, required=True, help="Atom labels like S2 N3 O4.")
    charges_parser.add_argument("--out", required=True, type=Path, help="Output CSV file path.")
    charges_parser.add_argument("--strict", action="store_true", help="Fail if no NBO charge data are present.")
    charges_parser.set_defaults(func=command_nbo_charges)

    wiberg_parser = subparsers.add_parser(
        "wiberg",
        help="Extract Wiberg bond indices; without --strict writes header-only when data are missing.",
    )
    wiberg_parser.add_argument("--input", required=True, type=Path, help="Input IRC file.")
    wiberg_parser.add_argument("--bonds", nargs="+", type=parse_bond_label, required=True, help="Bond labels like S2-N3 N3-O4.")
    wiberg_parser.add_argument("--out", required=True, type=Path, help="Output CSV file path.")
    wiberg_parser.add_argument("--strict", action="store_true", help="Fail if no Wiberg bond index data are present.")
    wiberg_parser.set_defaults(func=command_wiberg)

    bond_orb_parser = subparsers.add_parser(
        "bond-orbitals",
        help="Extract bond orbital information; without --strict writes empty JSON when data are missing.",
    )
    bond_orb_parser.add_argument("--input", required=True, type=Path, help="Input IRC file.")
    bond_orb_parser.add_argument("--keys", nargs="+", required=True, help="Bond orbital keys, e.g., \"S2-N3\".")
    bond_orb_parser.add_argument("--out", required=True, type=Path, help="Output JSON file path.")
    bond_orb_parser.add_argument("--strict", action="store_true", help="Fail if no bond orbital data are present.")
    bond_orb_parser.set_defaults(func=command_bond_orbitals)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(args.verbose)

    try:
        return args.func(args)
    except FileNotFoundError:
        logger.error("Input file not found: %s", args.input)
        return 1
    except (ParseError, ValueError, RuntimeError) as exc:
        logger.error("%s", exc)
        return 1
    except Exception:
        logger.exception("Unexpected error during analysis")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
