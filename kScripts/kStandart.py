"""Generate standard IRC analysis tables using :class:`kudi.analysis.irc_path.IRCPath`."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Sequence

import numpy as np

from kudi.analysis.irc_path import IRCPath
from kudi.exceptions import ParseError

logger = logging.getLogger(__name__)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute standard IRC tables from a Gaussian IRC SP output file.")
    parser.add_argument("--input", required=True, type=Path, help="Path to the IRC single-point output (.dat).")
    parser.add_argument("--outdir", required=True, type=Path, help="Directory where analysis tables will be written.")
    parser.add_argument(
        "--reference",
        choices=["min_rx", "first"],
        default="min_rx",
        help="Reference point for relative energies (default: min_rx).",
    )
    parser.add_argument("--verbose", action="store_true", help="Increase log verbosity.")
    return parser.parse_args(argv)


def write_dat(path: Path, header: str, x: Sequence[float], y: Sequence[float]) -> None:
    if len(x) != len(y):
        raise ValueError(f"Mismatched data lengths for {path.name}: {len(x)} rx vs {len(y)} values")
    lines = [header]
    for rx_val, value in zip(x, y):
        lines.append(f"{rx_val:.10g} {value:.10g}")
    content = "\n".join(lines) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def compute_tables(path: IRCPath, reference: str, outdir: Path) -> None:
    rx = np.asarray(path.rx_coords, dtype=float)
    logger.debug("Loaded %d reaction coordinates", rx.size)

    rel_energy = np.asarray(path.relative_energies_kcal(reference=reference), dtype=float)
    write_dat(outdir / "energy.dat", "# rx rel_energy_kcal_mol", rx, rel_energy)

    force_data = path.reaction_force()
    write_dat(outdir / "force.dat", "# rx reaction_force", force_data["reaction_coordinate"], force_data["reaction_force"])

    mu_data = path.chemical_potential_koopmans()
    write_dat(
        outdir / "chemPot_koopmans.dat",
        "# rx chemical_potential_koopmans_kcal_mol",
        mu_data["reaction_coordinate"],
        mu_data["chemical_potential"],
    )

    flux_data = path.flux()
    write_dat(outdir / "flux_koopmans.dat", "# rx flux_koopmans", flux_data["reaction_coordinate"], flux_data["flux"])


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

    try:
        irc_path = IRCPath.from_file(args.input)
        compute_tables(irc_path, args.reference, args.outdir)
    except FileNotFoundError:
        logger.error("Input file not found: %s", args.input)
        return 1
    except (ParseError, ValueError) as exc:
        logger.error("Failed to process IRC file: %s", exc)
        return 1
    except Exception:
        logger.exception("Unexpected error during IRC analysis")
        return 1

    logger.info("Analysis tables written to %s", args.outdir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

