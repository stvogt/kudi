from kudi.parsing.irc import extract_rx_from_anchor_line, segment_irc_blocks


def test_segment_irc_blocks_counts_blocks(irc_blocks):
    anchor = "Single Point computation for reaction coordinate:"
    assert len(irc_blocks) > 1

    rx_coords = []
    for block in irc_blocks:
        assert block
        assert anchor in block[0]
        rx_coords.append(extract_rx_from_anchor_line(block[0]))

    assert len(rx_coords) == len(irc_blocks)
    assert all(isinstance(rx, float) for rx in rx_coords)
    assert any(rx != rx_coords[0] for rx in rx_coords[1:])
    diffs = [b - a for a, b in zip(rx_coords, rx_coords[1:])]
    monotonic_increasing = all(diff >= 0 for diff in diffs)
    monotonic_decreasing = all(diff <= 0 for diff in diffs)
    assert monotonic_increasing or monotonic_decreasing


def test_extract_rx_from_anchor_line_parses_float():
    line = " Single Point computation for reaction coordinate:   -0.1000"
    assert extract_rx_from_anchor_line(line) == -0.1


def test_segment_handles_blank_lines_and_trailing_text():
    lines = [
        "header",
        "",
        " Single Point computation for reaction coordinate:   -0.5000",
        " data line a",
        "",
        " Single Point computation for reaction coordinate:   0.0000",
        " data line b",
        " tail",
    ]

    blocks = segment_irc_blocks(lines)

    assert len(blocks) == 2
    assert blocks[0][0].strip().startswith("Single Point computation")
    assert blocks[-1][-1].strip() == "tail"
