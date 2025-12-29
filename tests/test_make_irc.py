from pathlib import Path

from kudi.gaussian_irc import IrcOptions, assemble_irc_input, load_xyz_geometry


def test_assemble_irc_input_builds_link1_sections(tmp_path: Path) -> None:
    xyz_path = tmp_path / "geom.xyz"
    xyz_path.write_text(
        "\n".join(
            [
                "3",
                "comment",
                "H 0.0 0.0 0.0",
                "O 0.0 0.0 1.0",
                "H 0.0 1.0 0.0",
            ]
        )
    )

    options = IrcOptions(
        direction="both",
        maxpoints=50,
        stepsize=5,
        maxcycle=20,
        force_constants="CalcFC",
        phase=[1, 2],
        tight="VeryTight",
    )

    geometry = load_xyz_geometry(xyz_path)

    text = assemble_irc_input(
        base_route="#P wb97xd/def2TZVP scf=tight",
        options=options,
        geometry_lines=geometry,
        title="IRC computation",
        charge=0,
        multiplicity=1,
        chk="IRC.chk",
        mem="4GB",
        nproc=8,
    )

    assert "irc=(Reverse,MaxPoints=50,StepSize=5,MaxCycle=20,CalcFC,Phase=(1,2),VeryTight)" in text
    assert "irc=(Forward,MaxPoints=50,StepSize=5,MaxCycle=20,CalcFC,Phase=(1,2),VeryTight)" in text
    assert "--Link1--" in text
    assert "O 0.0 0.0 1.0" in text
