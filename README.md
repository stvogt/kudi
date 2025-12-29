# Kudi

Kudi is a Python package for extracting key properties from Gaussian intrinsic reaction coordinate (IRC) output files. The library focuses on pure data extraction and analysis so it can be used from scripts or notebooks without side effects.

## Supported inputs
- Gaussian IRC outputs that contain single-point computations along a reaction path
- Optional Natural Bond Orbital (NBO) analysis sections within the same Gaussian output

## Installation

Install in editable mode for development:

```bash
pip install -e ".[dev]"
```

Install for regular use:

```bash
pip install .
```

Install with notebook tooling:

```bash
pip install -e ".[notebook]"
```

Run the test suite after installing development extras:

```bash
pytest
```

## Usage

Parse an IRC output and access energies, geometries, and NBO-derived properties:

```python
from pathlib import Path
from kudi import IRCPath

irc = IRCPath.from_file(Path("path/to/irc_output.log"))
print(irc.rx_coords)
print(irc.relative_energies_kcal())
```

## Example Gaussian IRC input

The repository includes a ready-to-run dual-direction Gaussian IRC input for the
HSNO geometry at `examples/hsno_irc_input.gjf`. It was generated from the XYZ
coordinates in `examples/hsno.xyz` with a WB97XD/def2TZVP route, tight SCF, an
UltraFine grid, and VeryTight IRC convergence.

You can regenerate the file (or produce your own) with the CLI:

```bash
python driver/make_irc.py \
  --xyz examples/hsno.xyz \
  --method wb97xd --basis def2TZVP \
  --route-extra "scf=tight Int=UltraFine" \
  --maxpoints 40 --stepsize 8 --maxcycle 40 --phase 1 2 \
  --verytight --fc CalcFC --chk hsno_irc.chk --mem 8GB \
  --outdir examples --title "HSNO IRC example"
```

By default this writes a two-Link1 input (`input_irc.dat`) containing reverse
and forward paths.

## Derived IRC quantities

The :class:`~kudi.IRCPath` API also exposes reaction force, reaction force constant, Koopmans chemical potential, and flux as arrays aligned with the reaction coordinate for direct plotting in notebooks.
