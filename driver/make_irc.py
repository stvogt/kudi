from __future__ import annotations

import argparse
from pathlib import Path

from kudi.gaussian_irc import (
    IrcOptions,
    assemble_irc_input,
    load_xyz_geometry,
    parse_isotopes_file,
    parse_report_read_file,
)


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be a positive integer")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate Gaussian IRC inputs")

    parser.add_argument("--xyz", required=True, type=Path, help="Path to XYZ geometry")

    parser.add_argument("--route", help="Full Gaussian route section (without IRC)")
    parser.add_argument("--method", help="Electronic structure method")
    parser.add_argument("--basis", help="Basis set")

    parser.add_argument("--charge", type=int, default=0, help="Molecular charge")
    parser.add_argument("--mult", type=int, default=1, help="Multiplicity")
    parser.add_argument("--nprocs", type=int, default=8, help="Number of processors")
    parser.add_argument("--mem", default="4GB", help="Memory allocation (Gaussian syntax)")
    parser.add_argument("--chk", default="IRC.chk", help="Checkpoint file name")
    parser.add_argument("--title", default="IRC computation", help="Job title")
    parser.add_argument("--outdir", default="irc", type=Path, help="Output directory")

    direction = parser.add_mutually_exclusive_group()
    direction.add_argument("--forward", action="store_true", help="Forward IRC only")
    direction.add_argument("--reverse", action="store_true", help="Reverse IRC only")
    direction.add_argument("--both", action="store_true", help="Forward and reverse IRC")
    direction.add_argument("--downhill", action="store_true", help="Downhill IRC")
    direction.add_argument("--downhill-mode", action="store_true", help="Alias for downhill")

    parser.add_argument("--phase", nargs="+", type=int, help="Phase vector (2-4 integers)")
    parser.add_argument("--maxpoints", type=positive_int, help="Maximum points")
    parser.add_argument("--stepsize", type=positive_int, help="Step size (0.01 Bohr units)")
    parser.add_argument("--maxcycle", type=positive_int, help="Maximum optimization cycles")
    parser.add_argument("--restart", action="store_true", help="Restart from checkpoint")

    parser.add_argument(
        "--algorithm",
        choices=["HPC", "EulerPC", "LQA", "DVV", "Euler"],
        help="IRC algorithm",
    )
    parser.add_argument("--gradient-only", action="store_true", help="GradientOnly option")
    parser.add_argument(
        "--coord",
        choices=["MassWeighted", "Cartesian"],
        help="Coordinate system",
    )
    parser.add_argument(
        "--fc",
        choices=["CalcFC", "RCFC", "CalcAll"],
        help="Force constant strategy",
    )
    parser.add_argument("--recalc", type=positive_int, help="ReCalc frequency")
    parser.add_argument("--recalc-predictor", type=positive_int, help="Predictor ReCalcFC")
    parser.add_argument("--recalc-corrector", type=positive_int, help="Corrector ReCalcFC")

    tight_group = parser.add_mutually_exclusive_group()
    tight_group.add_argument("--tight", action="store_true", help="Use Tight IRC convergence")
    tight_group.add_argument(
        "--verytight", action="store_true", help="Use VeryTight IRC convergence"
    )

    parser.add_argument(
        "--report",
        choices=["Bonds", "Angles", "Dihedrals", "Cartesians", "All"],
        help="Report option",
    )
    parser.add_argument("--report-read", type=Path, help="Path to Report=Read atoms list")

    parser.add_argument(
        "--recorrect",
        choices=["Yes", "Never", "Always", "Test"],
        help="ReCorrect setting",
    )

    parser.add_argument(
        "--read-isotopes",
        action="store_true",
        help="Include ReadIsotopes keyword and payload",
    )
    parser.add_argument(
        "--isotopes-file",
        type=Path,
        help="File containing ReadIsotopes payload",
    )

    parser.add_argument("--route-extra", help="Additional tokens to append to route")

    return parser


def resolve_direction(args: argparse.Namespace) -> str:
    if args.downhill or args.downhill_mode:
        return "downhill"
    if args.forward:
        return "forward"
    if args.reverse:
        return "reverse"
    return "both"


def validate_args(args: argparse.Namespace) -> None:
    if not args.route and (not args.method or not args.basis):
        raise SystemExit("Either --route or both --method and --basis are required")

    if args.phase is not None and not (2 <= len(args.phase) <= 4):
        raise SystemExit("--phase requires between 2 and 4 integers")

    if (args.recalc_predictor is None) != (args.recalc_corrector is None):
        raise SystemExit("--recalc-predictor and --recalc-corrector must be used together")

    if args.report_read and args.report:
        raise SystemExit("Use either --report or --report-read, not both")

    if args.read_isotopes and not args.isotopes_file:
        raise SystemExit("--read-isotopes requires --isotopes-file")

    if args.isotopes_file and not args.read_isotopes:
        raise SystemExit("--isotopes-file requires --read-isotopes")


def build_base_route(args: argparse.Namespace) -> str:
    if args.route:
        base_route = args.route.strip()
    else:
        base_route = f"#P {args.method}/{args.basis}"

    if args.route_extra:
        base_route = f"{base_route} {args.route_extra.strip()}"

    if args.verytight and "int=" not in base_route.lower():
        base_route = f"{base_route} Int=UltraFine"

    return base_route.strip()


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    validate_args(args)

    direction = resolve_direction(args)

    irc_options = IrcOptions(
        direction=direction,
        maxpoints=args.maxpoints,
        stepsize=args.stepsize,
        maxcycle=args.maxcycle,
        phase=args.phase,
        algorithm=args.algorithm,
        gradient_only=args.gradient_only,
        coord_system=args.coord,
        force_constants=args.fc,
        recalc=args.recalc,
        recalc_predictor=args.recalc_predictor,
        recalc_corrector=args.recalc_corrector,
        restart=args.restart,
        tight="VeryTight" if args.verytight else "Tight" if args.tight else None,
        report="Read" if args.report_read else args.report,
        report_read_atoms=parse_report_read_file(args.report_read)
        if args.report_read
        else None,
        recorrect=args.recorrect,
    )

    geometry_lines = load_xyz_geometry(args.xyz)

    isotopes_payload = (
        parse_isotopes_file(args.isotopes_file) if args.read_isotopes else None
    )

    base_route = build_base_route(args)

    if args.read_isotopes:
        base_route = f"{base_route} ReadIsotopes"

    gaussian_text = assemble_irc_input(
        base_route=base_route,
        options=irc_options,
        geometry_lines=geometry_lines,
        title=args.title,
        charge=args.charge,
        multiplicity=args.mult,
        chk=args.chk,
        mem=args.mem,
        nproc=args.nprocs,
        read_isotopes=isotopes_payload,
        report_read_atoms=irc_options.report_read_atoms,
    )

    output_dir: Path = args.outdir
    output_dir.mkdir(parents=True, exist_ok=True)

    if direction == "both":
        outfile = output_dir / "input_irc.dat"
    elif direction == "forward":
        outfile = output_dir / "input_forward.dat"
    elif direction == "reverse":
        outfile = output_dir / "input_reverse.dat"
    else:
        outfile = output_dir / "input_downhill.dat"

    outfile.write_text(gaussian_text)


if __name__ == "__main__":
    main()
