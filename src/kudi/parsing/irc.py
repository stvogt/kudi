"""Segment Gaussian IRC outputs into blocks."""

from typing import List

from ..exceptions import ParseError

ANCHOR = "Single Point computation for reaction coordinate:"


def extract_rx_from_anchor_line(line: str) -> float:
    """Extract the reaction coordinate from an anchor line."""

    parts = line.strip().split()
    if not parts:
        raise ParseError("Empty anchor line")
    try:
        return float(parts[-1])
    except ValueError as exc:
        raise ParseError(f"Could not parse reaction coordinate from line: {line}") from exc


def segment_irc_blocks(lines: List[str], *, strict: bool = True) -> List[List[str]]:
    """Split an IRC output into blocks using the anchor lines."""

    anchor_indices: List[int] = []
    for idx, line in enumerate(lines):
        if ANCHOR in line:
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
