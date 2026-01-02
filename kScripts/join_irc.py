"""Concatenate IRC log fragments."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Concatenate reverse and forward IRC logs.")
    parser.add_argument("--reverse", required=True, type=Path, help="Path to the reverse IRC log.")
    parser.add_argument("--forward", required=True, type=Path, help="Path to the forward IRC log.")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("output.log"),
        help="Output log path (default: output.log in the current directory).",
    )
    parser.add_argument("--verbose", action="store_true", help="Increase log verbosity.")
    return parser.parse_args(argv)


def concatenate_logs(reverse_path: Path, forward_path: Path, output_path: Path) -> None:
    if not reverse_path.is_file():
        raise FileNotFoundError(f"Reverse log not found: {reverse_path}")
    if not forward_path.is_file():
        raise FileNotFoundError(f"Forward log not found: {forward_path}")

    logger.debug("Reading reverse log from %s", reverse_path)
    reverse_bytes = reverse_path.read_bytes()
    logger.debug("Reading forward log from %s", forward_path)
    forward_bytes = forward_path.read_bytes()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    logger.debug("Writing concatenated log to %s", output_path)
    output_path.write_bytes(reverse_bytes + forward_bytes)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

    try:
        concatenate_logs(args.reverse, args.forward, args.out)
    except FileNotFoundError as exc:
        logger.error(exc)
        return 1
    except Exception:
        logger.exception("Unexpected error while concatenating IRC logs")
        return 1

    logger.info("Concatenation complete: %s", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
