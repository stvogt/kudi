from pathlib import Path

from kudi.parsing.irc import extract_rx_from_anchor_line, segment_irc_blocks
from kudi.io import read_lines


def test_segment_irc_blocks_counts_blocks():
    lines = read_lines(Path("tests/fixtures/gaussian_irc.log"))
    blocks = segment_irc_blocks(lines)
    assert len(blocks) == 2


def test_extract_rx_from_anchor_line_parses_float():
    line = " Single Point computation for reaction coordinate:   -0.1000"
    assert extract_rx_from_anchor_line(line) == -0.1
