"""Basic IO utilities."""

from pathlib import Path
import gzip
from typing import List, Union


def read_lines(path: Union[str, Path]) -> List[str]:
    """Read text lines from a file, transparently handling gzip files."""

    file_path = Path(path)
    if file_path.suffix == ".gz":
        with gzip.open(file_path, "rt", encoding="utf-8") as handle:
            return handle.read().splitlines()
    with file_path.open("r", encoding="utf-8") as handle:
        return handle.read().splitlines()
