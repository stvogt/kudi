from __future__ import annotations

import importlib.util
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = PROJECT_ROOT / "tests" / "fixtures" / "cf3+f.dat"


def load_script(name: str):
    script_path = PROJECT_ROOT / "kScripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, script_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def count_data_lines(path: Path) -> int:
    content = path.read_text().strip().splitlines()
    return len(content)


def test_join_irc_concatenation(tmp_path):
    join_irc = load_script("join_irc")

    reverse_path = tmp_path / "reverse.log"
    forward_path = tmp_path / "forward.log"
    output_path = tmp_path / "output.log"

    reverse_bytes = b"reverse\n123\n"
    forward_bytes = b"forward\n456\n"
    reverse_path.write_bytes(reverse_bytes)
    forward_path.write_bytes(forward_bytes)

    result = join_irc.main(
        ["--reverse", str(reverse_path), "--forward", str(forward_path), "--out", str(output_path)]
    )
    assert result == 0
    assert output_path.read_bytes() == reverse_bytes + forward_bytes


def test_kstandart_outputs(tmp_path):
    kstandart = load_script("kStandart")
    outdir = tmp_path / "analysis"

    result = kstandart.main(["--input", str(FIXTURE_PATH), "--outdir", str(outdir)])
    assert result == 0

    expected_files = [
        "energy.dat",
        "force.dat",
        "chemPot_koopmans.dat",
        "flux_koopmans.dat",
    ]
    for filename in expected_files:
        path = outdir / filename
        assert path.exists()
        assert count_data_lines(path) > 1


def test_ktemplate_energy_force_mu(tmp_path):
    ktemplate = load_script("kTemplate")

    energy_out = tmp_path / "energy.dat"
    force_out = tmp_path / "force.dat"
    mu_out = tmp_path / "mu.dat"

    assert ktemplate.main(["energy", "--input", str(FIXTURE_PATH), "--out", str(energy_out)]) == 0
    assert ktemplate.main(["force", "--input", str(FIXTURE_PATH), "--out", str(force_out)]) == 0
    assert ktemplate.main(["mu-koopmans", "--input", str(FIXTURE_PATH), "--out", str(mu_out)]) == 0

    for path in (energy_out, force_out, mu_out):
        assert path.exists()
        assert count_data_lines(path) > 1
