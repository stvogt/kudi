#!/opt/anaconda/anaconda3/envs/kudi/bin/python

import argparse
from pathlib import Path
from typing import List

def read_lines(filepath: Path) -> List[str]:
    """
    Read lines from a file.

    Args:
    filepath (Path): Path to the file to be read.

    Returns:
    List[str]: A list of lines read from the file.
    """
    with filepath.open('r') as file:
        return file.readlines()

def write_lines(lines: List[str], filepath: Path) -> None:
    """
    Write lines to a file.

    Args:
    lines (List[str]): Lines to be written to the file.
    filepath (Path): Path to the file where lines will be written.
    """
    with filepath.open('w') as file:
        for line in lines:
            file.write(line)

def main(rev_path: Path, forw_path: Path, output_path: Path) -> None:
    """
    Process reverse and forward IRC files and combine their contents into an output file.

    Args:
    rev_path (Path): Path to the reverse IRC file.
    forw_path (Path): Path to the forward IRC file.
    output_path (Path): Path to the output file.
    """
    irc_rev_lines = read_lines(rev_path)
    irc_forw_lines = read_lines(forw_path)

    combined_lines = irc_rev_lines + irc_forw_lines
    write_lines(combined_lines, output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process IRC paths.")
    parser.add_argument("rev", type=Path, help="Path to the reverse IRC file")
    parser.add_argument("forw", type=Path, help="Path to the forward IRC file")
    parser.add_argument("-o", "--output", type=Path, default=Path("output.log"),
                        help="Path to the output file")

    args = parser.parse_args()

    main(args.rev, args.forw, args.output)

