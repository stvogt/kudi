from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal


Direction = Literal["forward", "reverse", "both", "downhill"]
Algorithm = Literal["HPC", "EulerPC", "LQA", "DVV", "Euler"]
CoordSystem = Literal["MassWeighted", "Cartesian"]
ForceConstants = Literal["CalcFC", "RCFC", "CalcAll"]
Tightness = Literal[None, "Tight", "VeryTight"]
Report = Literal[
    None,
    "Read",
    "Bonds",
    "Angles",
    "Dihedrals",
    "Cartesians",
    "All",
]
ReCorrect = Literal[None, "Yes", "Never", "Always", "Test"]


@dataclass
class IrcOptions:
    direction: Direction = "both"
    maxpoints: int | None = None
    stepsize: int | None = None
    maxcycle: int | None = None
    phase: list[int] | None = None
    algorithm: Algorithm | None = None
    gradient_only: bool = False
    coord_system: CoordSystem | None = None
    force_constants: ForceConstants | None = None
    recalc: int | None = None
    recalc_predictor: int | None = None
    recalc_corrector: int | None = None
    restart: bool = False
    tight: Tightness = None
    report: Report = None
    report_read_atoms: list[list[int]] | None = None
    recorrect: ReCorrect = None


def build_irc_keyword(opts: IrcOptions, *, direction_override: Direction | None = None) -> str:
    """Assemble the irc=() keyword string from structured options."""

    direction = direction_override or opts.direction
    items: list[str] = []

    if direction == "forward":
        items.append("Forward")
    elif direction == "reverse":
        items.append("Reverse")
    elif direction == "downhill":
        items.append("Downhill")

    if opts.maxpoints is not None:
        items.append(f"MaxPoints={opts.maxpoints}")
    if opts.stepsize is not None:
        items.append(f"StepSize={opts.stepsize}")
    if opts.maxcycle is not None:
        items.append(f"MaxCycle={opts.maxcycle}")

    if opts.force_constants is not None:
        items.append(opts.force_constants)

    if opts.algorithm is not None:
        items.append(opts.algorithm)

    if opts.gradient_only:
        items.append("GradientOnly")

    if opts.coord_system is not None:
        items.append(opts.coord_system)

    if opts.phase is not None:
        phase_values = ",".join(str(v) for v in opts.phase)
        items.append(f"Phase=({phase_values})")

    if opts.recalc is not None:
        items.append(f"ReCalc={opts.recalc}")
    elif opts.recalc_predictor is not None and opts.recalc_corrector is not None:
        items.append(
            f"ReCalcFC=(Predictor={opts.recalc_predictor},Corrector={opts.recalc_corrector})"
        )

    if opts.restart:
        items.append("Restart")

    if opts.report is not None:
        if opts.report == "All":
            items.append("Report")
        else:
            items.append(f"Report={opts.report}")

    if opts.recorrect is not None:
        items.append(f"ReCorrect={opts.recorrect}")

    if opts.tight is not None:
        items.append(opts.tight)

    return f"irc=({','.join(items)})"


def load_xyz_geometry(xyz_path: Path) -> list[str]:
    """Load geometry lines from an XYZ file.

    Supports standard XYZ format with a natoms header and comment line. If the
    first line contains two integers, it is treated as a Gaussian-style
    charge/multiplicity header and returned geometry starts from the second
    line.
    """

    contents = xyz_path.read_text().splitlines()
    if not contents:
        raise ValueError(f"XYZ file {xyz_path} is empty")

    first_tokens = contents[0].split()
    geometry_lines: list[str]

    if len(first_tokens) == 1 and first_tokens[0].isdigit():
        natoms = int(first_tokens[0])
        geometry_lines = contents[2 : 2 + natoms]
        if len(geometry_lines) < natoms:
            raise ValueError(f"XYZ file {xyz_path} is missing geometry lines")
    elif len(first_tokens) == 2 and all(token.lstrip("-+").isdigit() for token in first_tokens):
        geometry_lines = contents[1:]
    else:
        geometry_lines = contents

    return [" ".join(line.split()) for line in geometry_lines if line.strip()]


def render_gaussian_input(
    *,
    route_section: str,
    geometry_lines: Iterable[str],
    title: str,
    charge: int,
    multiplicity: int,
    chk: str,
    mem: str,
    nproc: int,
    read_isotopes: list[str] | None = None,
    report_read_atoms: list[list[int]] | None = None,
) -> str:
    lines: list[str] = [
        f"%NProcShared={nproc}",
        f"%Mem={mem}",
        f"%Chk={chk}",
        "",
        route_section.strip(),
        "",
        title,
        "",
        f"{charge} {multiplicity}",
    ]

    lines.extend(geometry_lines)
    lines.append("")

    if read_isotopes:
        lines.extend(read_isotopes)
        lines.append("")

    if report_read_atoms:
        lines.extend(" ".join(map(str, group)) for group in report_read_atoms)
        lines.append("")

    return "\n".join(lines)


def parse_report_read_file(path: Path) -> list[list[int]]:
    atoms: list[list[int]] = []
    for raw_line in path.read_text().splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        tokens = stripped.split()
        if not all(token.lstrip("-+").isdigit() for token in tokens):
            raise ValueError(
                f"Report read list {path} must contain only integers per line"
            )
        if len(tokens) > 4:
            raise ValueError("Report=Read lines support up to 4 atom indices")
        atoms.append([int(token) for token in tokens])
    if not atoms:
        raise ValueError(f"Report read list {path} is empty")
    return atoms


def parse_isotopes_file(path: Path) -> list[str]:
    lines = [line.strip() for line in path.read_text().splitlines() if line.strip()]
    if len(lines) < 2:
        raise ValueError("Isotopes file must include header and at least one mass line")
    return lines


def ensure_route_prefix(route: str) -> str:
    route = route.strip()
    if not route.startswith("#"):
        return f"#P {route}"
    return route


def make_link1_section(
    *,
    base_route: str,
    irc_keyword: str,
    geometry_lines: Iterable[str],
    title: str,
    charge: int,
    multiplicity: int,
    chk: str,
    mem: str,
    nproc: int,
    read_isotopes: list[str] | None,
    report_read_atoms: list[list[int]] | None,
) -> str:
    route_section = f"{ensure_route_prefix(base_route)} {irc_keyword}"
    return render_gaussian_input(
        route_section=route_section,
        geometry_lines=geometry_lines,
        title=title,
        charge=charge,
        multiplicity=multiplicity,
        chk=chk,
        mem=mem,
        nproc=nproc,
        read_isotopes=read_isotopes,
        report_read_atoms=report_read_atoms,
    )


def assemble_irc_input(
    *,
    base_route: str,
    options: IrcOptions,
    geometry_lines: Iterable[str],
    title: str,
    charge: int,
    multiplicity: int,
    chk: str,
    mem: str,
    nproc: int,
    read_isotopes: list[str] | None = None,
    report_read_atoms: list[list[int]] | None = None,
) -> str:
    if options.direction == "both":
        reverse_section = make_link1_section(
            base_route=base_route,
            irc_keyword=build_irc_keyword(options, direction_override="reverse"),
            geometry_lines=geometry_lines,
            title=title,
            charge=charge,
            multiplicity=multiplicity,
            chk=chk,
            mem=mem,
            nproc=nproc,
            read_isotopes=read_isotopes,
            report_read_atoms=report_read_atoms,
        )
        forward_section = make_link1_section(
            base_route=base_route,
            irc_keyword=build_irc_keyword(options, direction_override="forward"),
            geometry_lines=geometry_lines,
            title=title,
            charge=charge,
            multiplicity=multiplicity,
            chk=chk,
            mem=mem,
            nproc=nproc,
            read_isotopes=read_isotopes,
            report_read_atoms=report_read_atoms,
        )
        return "\n--Link1--\n\n".join([reverse_section, forward_section]) + "\n"

    irc_keyword = build_irc_keyword(options)
    return (
        make_link1_section(
            base_route=base_route,
            irc_keyword=irc_keyword,
            geometry_lines=geometry_lines,
            title=title,
            charge=charge,
            multiplicity=multiplicity,
            chk=chk,
            mem=mem,
            nproc=nproc,
            read_isotopes=read_isotopes,
            report_read_atoms=report_read_atoms,
        )
        + "\n"
    )
