#! /usr/bin/python

"""Generate Gaussian16 single-point Link1 blocks from IRC output."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import kudi.gaussianPoint as gsp


@dataclass
class GeometryData:
    """Container for atomic numbers and coordinates."""

    atomic_numbers: list[str]
    x: list[str]
    y: list[str]
    z: list[str]


def build_argparser() -> argparse.ArgumentParser:
    """Construct the argument parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o",
        "--output-irc",
        dest="output_irc",
        type=Path,
        default=Path("output.log"),
        help="File with IRC output (default: output.log).",
    )
    parser.add_argument(
        "-i",
        "--input-sp",
        dest="input_sp",
        type=str,
        default="input_sp.dat",
        help="File name for single point inputs (default: input_sp.dat).",
    )
    parser.add_argument(
        "-a",
        "--folder",
        dest="folder",
        type=Path,
        default=Path("sp"),
        help="Destination folder for single point inputs (default: sp).",
    )
    parser.add_argument(
        "-p",
        "--numproc",
        dest="proc_num",
        default="4",
        help="Number of processors (default: 4).",
    )
    parser.add_argument(
        "-m",
        "--memory",
        dest="mem_num",
        default="2GB",
        help="Memory allotted for the computation (default: 2GB).",
    )
    parser.add_argument(
        "-s",
        "--scf",
        dest="scf",
        default="tight",
        help="SCF convergence criterion (default: tight).",
    )
    parser.add_argument(
        "-c",
        "--charge",
        dest="charge",
        default="0",
        help="Charge of the computation (default: 0).",
    )
    parser.add_argument(
        "-n",
        "--multiplicity",
        dest="multi",
        default="1",
        help="Multiplicity of the computation (default: 1).",
    )
    parser.add_argument(
        "-z",
        "--otheroption",
        dest="other",
        default="",
        help="Additional option to append to the route section.",
    )
    parser.add_argument(
        "-v",
        "--invert",
        dest="invert",
        action="store_true",
        help="Invert reaction coordinate sign.",
    )
    parser.add_argument(
        "--minus1",
        dest="minus",
        action="store_true",
        help="Multiply reaction coordinate by -1 (applied after --invert).",
    )
    parser.add_argument(
        "--pop",
        dest="population",
        default="NBORead",
        help="Population analysis (default: NBORead).",
    )
    parser.add_argument(
        "--pseudo",
        dest="pseudo",
        type=Path,
        default=None,
        help="Pseudo potential data file (default: None).",
    )

    chk_group = parser.add_mutually_exclusive_group()
    chk_group.add_argument(
        "--chk",
        dest="write_chk",
        action="store_true",
        default=True,
        help="Write checkpoint directives (default).",
    )
    chk_group.add_argument(
        "--no-chk",
        dest="write_chk",
        action="store_false",
        help="Disable checkpoint directives and folder creation.",
    )

    return parser


def parse_irc_geometries(lines: Iterable[str]) -> dict[float, GeometryData]:
    """Extract geometries keyed by reaction coordinate from IRC output lines."""

    coords_dict: dict[float, GeometryData] = {}
    first = True
    structures = False
    reverse = True
    xyz_re = re.compile(r"(\s+\d+){3}(\s+-?\d+\.\d+){3}")
    forward_re = re.compile(r".*forward[,\s]")
    inp_re = re.compile("Input orientation")
    zmat_re = re.compile("Z-Matrix orientation")

    atomic_numbers: list[str] = []
    x_coords: list[str] = []
    y_coords: list[str] = []
    z_coords: list[str] = []

    line_list = list(lines)
    for lnum, line in enumerate(line_list):
        match = xyz_re.search(line)
        if forward_re.search(line):
            reverse = False
        if inp_re.search(line) or zmat_re.search(line):
            structures = True
            atomic_numbers = []
            x_coords = []
            y_coords = []
            z_coords = []
        if match and structures:
            atomic_numbers.append(line.split()[1])
            x_coords.append(line.split()[3])
            y_coords.append(line.split()[4])
            z_coords.append(line.split()[5])
            if lnum + 1 < len(line_list) and "--------------" in line_list[lnum + 1]:
                if first:
                    coords_dict[0.0000] = GeometryData(
                        atomic_numbers, x_coords, y_coords, z_coords
                    )
                    first = False
                structures = False
        if "NET REACTION COORDINATE UP TO THIS POINT" in line:
            if reverse:
                rx_coord = -1 * float(line.split()[8])
            else:
                rx_coord = float(line.split()[8])
            coords_dict[rx_coord] = GeometryData(
                atomic_numbers, x_coords, y_coords, z_coords
            )

    return coords_dict


def write_sp_link1(
    out_path: Path,
    geoms: dict[float, GeometryData],
    *,
    proc_num: str,
    mem_num: str,
    scf: str,
    charge: str,
    multi: str,
    invert: bool,
    minus: bool,
    population: str,
    pseudo: Path | None,
    other: str,
    write_chk: bool,
    theory: str,
    basis: str,
) -> int:
    """Write Link1 single-point inputs to the provided path."""

    out_path.parent.mkdir(parents=True, exist_ok=True)
    if write_chk:
        (out_path.parent / "CHK").mkdir(parents=True, exist_ok=True)

    pseudo_text = None
    if pseudo is not None:
        pseudo_text = pseudo.read_text()

    count = 0
    sorted_rx = sorted(geoms.keys())
    with out_path.open("w", encoding="utf-8") as handle:
        for idx, rxc in enumerate(sorted_rx):
            rx_value = rxc
            if invert:
                rx_value *= -1
            if minus:
                rx_value *= -1

            handle.write(f"%NProcShared={proc_num}\n")
            handle.write(f"%Mem={mem_num}\n")
            if write_chk:
                handle.write(f"%chk=CHK/sp_{count:03d}.chk\n")
            route = f"#P  {theory}/{basis} pop={population}  scf={scf}"
            if other:
                route = f"{route} {other}"
            handle.write(f"{route}\n\n")
            handle.write(
                f"Single Point computation for reaction coordinate: {rx_value}\n\n{charge} {multi}\n"
            )

            coords = geoms[rxc]
            for i in range(len(coords.atomic_numbers)):
                handle.write(
                    f"{coords.atomic_numbers[i]}    {coords.x[i]}    {coords.y[i]}    {coords.z[i]}\n"
                )
            handle.write("\n")

            if pseudo_text is not None:
                handle.write(pseudo_text)

            if "NBO" in population:
                handle.write("\n$nbo bndidx $end\n")

            if idx != len(sorted_rx) - 1:
                handle.write("\n--Link1--\n")
            else:
                handle.write("\n\n")
            count += 1

    return count


def main(argv: list[str] | None = None) -> int:
    """Entrypoint for command-line execution."""

    parser = build_argparser()
    args = parser.parse_args(argv)

    irc_lines = args.output_irc.read_text().splitlines()
    geometries = parse_irc_geometries(irc_lines)

    if not geometries:
        print("No geometries found in IRC output.", file=sys.stderr)
        return 1

    theory = gsp.get_level_of_theory(irc_lines)
    basis = gsp.get_basis(irc_lines)

    out_path = args.folder / args.input_sp
    blocks_written = write_sp_link1(
        out_path,
        geometries,
        proc_num=args.proc_num,
        mem_num=args.mem_num,
        scf=args.scf,
        charge=args.charge,
        multi=args.multi,
        invert=args.invert,
        minus=args.minus,
        population=args.population,
        pseudo=args.pseudo,
        other=args.other,
        write_chk=args.write_chk,
        theory=theory,
        basis=basis,
    )

    print(
        f"Input file containing {blocks_written} inputs was written to --->  {out_path}"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
