# Kudi

Kudi is a Python package for extracting key properties from Gaussian intrinsic reaction coordinate (IRC) output files. The library focuses on pure data extraction and analysis so it can be used from scripts or notebooks without side effects.

## Supported inputs
- Gaussian IRC outputs that contain single-point computations along a reaction path
- Optional Natural Bond Orbital (NBO) analysis sections within the same Gaussian output

## Not supported
- ORCA outputs
- Density data generation
- Plotting utilities or automatic file writes

## Installation

Install in editable mode for development:

```bash
pip install -e .
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
