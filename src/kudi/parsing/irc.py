"""Segment Gaussian IRC outputs into blocks."""

import re
from typing import List

from ..exceptions import ParseError

ANCHOR = "Single Point computation for reaction coordinate:"
ANCHOR_PATTERN = re.compile(r"^\s*" + re.escape(ANCHOR), re.IGNORECASE)


def extract_rx_from_anchor_line(line: str) -> float:
    """Extract the reaction coordinate from an anchor line."""

    pattern = re.compile(r"reaction coordinate:\s*([+-]?[0-9]*\.?[0-9]+(?:[Ee][+-]?[0-9]+)?)", re.IGNORECASE)
    match = pattern.search(line)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass

    for token in line.split():
        cleaned = token.strip("\\,")
        try:
            return float(cleaned)
        except ValueError:
            continue
    raise ParseError(f"Could not parse reaction coordinate from line: {line}")


def segment_irc_blocks(lines: List[str], *, strict: bool = True) -> List[List[str]]:
    """Split an IRC output into blocks using the anchor lines."""

    anchor_indices: List[int] = []
    for idx, line in enumerate(lines):
        if ANCHOR_PATTERN.search(line):
            anchor_indices.append(idx)

    if not anchor_indices:
        if strict:
            raise ParseError("No IRC points found in file")
        return []

    blocks: List[List[str]] = []
    for i, start in enumerate(anchor_indices):
        end = anchor_indices[i + 1] if i + 1 < len(anchor_indices) else len(lines)
        blocks.append(lines[start:end])
    return blocks
