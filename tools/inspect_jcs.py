"""Inspect .jcs file header and content snippets."""

import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def read_snippet(path: Path, length: int = 256) -> bytes | None:
    """Return the first `length` bytes of the file, or None on error."""
    try:
        with path.open("rb") as fh:
            return fh.read(length)
    except Exception as exc:
        logging.error("Failed to read %s: %s", path, exc)
        return None


def main() -> int:
    """"""
    if len(sys.argv) < 2:
        logging.error("Please provide a path to a .jcs file")
        return 2
    p = Path(sys.argv[1])
    if not p.exists():
        logging.error("File not found: %s", p)
        return 1
    snippet = read_snippet(p)
    if snippet is None:
        return 1
    logging.info("File: %s", p)
    logging.info("Size: %d bytes", p.stat().st_size)
    # show printable header + hex preview
    try:
        printable = snippet.decode("utf-8", errors="replace")
    except Exception:
        printable = "<binary>"
    logging.info("First bytes (utf-8 preview):\n%s", printable)
    logging.info("Hex preview:\n%s", snippet.hex())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
