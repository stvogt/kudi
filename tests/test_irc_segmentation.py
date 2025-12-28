from kudi.parsing.irc import extract_rx_from_anchor_line


def test_segment_irc_blocks_counts_blocks(irc_blocks):
    anchor = "Single Point computation for reaction coordinate:"
    assert len(irc_blocks) > 20

    rx_coords = []
    for block in irc_blocks:
        assert block
        assert anchor in block[0]
        rx_coords.append(extract_rx_from_anchor_line(block[0]))

    assert len(rx_coords) == len(irc_blocks)
    assert all(isinstance(rx, float) for rx in rx_coords)
    assert any(rx != rx_coords[0] for rx in rx_coords[1:])


def test_extract_rx_from_anchor_line_parses_float():
    line = " Single Point computation for reaction coordinate:   -0.1000"
    assert extract_rx_from_anchor_line(line) == -0.1
