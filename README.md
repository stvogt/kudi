# Kudi

<p align="center">
  <img src="KudiLogo.png" alt="Kudi logo" width="220">
</p>

## What is Kudi?

Kudi is a Python package for extracting key properties from Gaussian intrinsic reaction coordinate (IRC) single-point outputs. It parses IRC geometries and energies and exposes analysis-friendly access to properties as functions of the reaction coordinate (`rx`), with notebooks and tutorials to guide typical workflows.

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

## Quickstart

Parse an IRC output and access energies, forces, and electronic properties with the `IRCPath` API:

```python
from kudi import IRCPath

path = IRCPath.from_file("path/to/irc_output.log")
energies = path.relative_energies_kcal()
force = path.reaction_force()
mu = path.chemical_potential_koopmans()
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

## Implemented properties along reaction coordinate

| Property (vs rx) | API |
|---|---|
| Relative energy (kcal/mol) | `IRCPath.relative_energies_kcal(...)` |
| Reaction force (kcal/mol·rx⁻¹) | `IRCPath.reaction_force()` |
| Reaction force constant | `IRCPath.reaction_force_constant()` |
| Koopmans chemical potential (kcal/mol) | `IRCPath.chemical_potential_koopmans()` |
| Flux (−dμ/dξ) | `IRCPath.flux()` |
| NBO charges | `IRCPath.nbo_charges(...)` |
| Wiberg bond orders | `IRCPath.wiberg_bond_orders(...)` |
| Bond orbitals | `IRCPath.bond_orbitals(...)` |

All quantities are aligned with `reaction_coordinate` arrays for direct plotting or further numerical analysis.

## Tutorials

Explore worked examples in the tutorials directory:

- [CF₃ + F reaction: energies, forces, and flux](tutorials/tutorial_cf3f.ipynb)
- [HSNO isomerization: energies, forces, NBO charges, and Wiberg bond orders](tutorials/tutorial_hsno_isomerization.ipynb)
