import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture(scope="session")
def irc_fixture_path() -> Path:
    return ROOT / "tests" / "fixtures" / "output_sp.dat"


@pytest.fixture(scope="session")
def irc_lines(irc_fixture_path):
    from kudi.io import read_lines

    return read_lines(irc_fixture_path)


@pytest.fixture(scope="session")
def irc_blocks(irc_lines):
    from kudi.parsing.irc import segment_irc_blocks

    return segment_irc_blocks(irc_lines)


@pytest.fixture(scope="session")
def irc_path_obj(irc_fixture_path):
    from kudi import IRCPath

    return IRCPath.from_file(irc_fixture_path)
