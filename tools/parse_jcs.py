"""
Inspect .jcs files and try to identify numeric tables.

This script:
- shows basic metadata (size)
- prints printable ASCII runs
- samples 4-byte groups as floats (little & big endian) and scores plausibility

Usage:
    python tools/parse_jcs.py /path/to/file.jcs
"""
from __future__ import annotations

import argparse
import logging
import struct
from collections.abc import Iterable
from pathlib import Path
from statistics import mean, pstdev

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def find_ascii_runs(data: bytes, min_len: int = 4) -> list[str]:
    """
    Return contiguous ASCII runs of length >= min_len found in data.

    Args:
        data: Raw file bytes.
        min_len: Minimum length of ASCII run.

    Returns:
        List of decoded ASCII substrings.
    """
    runs: list[str] = []
    cur: bytearray = bytearray()
    for b in data:
        if 32 <= b < 127:
            cur.append(b)
        else:
            if len(cur) >= min_len:
                runs.append(cur.decode("ascii", errors="replace"))
            cur.clear()
    if len(cur) >= min_len:
        runs.append(cur.decode("ascii", errors="replace"))
    return runs


def sample_floats(data: bytes, offset: int = 0, count: int = 32, endian: str = "<") -> list[float]:
    """
    Interpret a slice of data as `count` IEEE-754 floats starting at offset.

    Args:
        data: Raw bytes.
        offset: Start offset in bytes.
        count: Number of floats to parse.
        endian: '<' for little endian, '>' for big endian.

    Returns:
        List of parsed floats (length may be fewer if data truncated).
    """
    floats: list[float] = []
    fmt = endian + "f"
    end = min(len(data), offset + count * 4)
    for i in range(offset, end, 4):
        chunk = data[i : i + 4]
        if len(chunk) < 4:
            break
        try:
            (v,) = struct.unpack(fmt, chunk)
        except struct.error:
            break
        floats.append(v)
    return floats


def score_float_list(values: Iterable[float]) -> float:
    """
    Score a list of floats for 'plausibility'.

    Heuristic: prefer lists with many finite values and moderate standard deviation.
    """
    vals = [v for v in values if not (v != v or v == float("inf") or v == float("-inf"))]  # filter NaN/inf
    if not vals:
        return 0.0
    # prefer values that are reasonably sized (not all huge)
    avg = abs(mean(vals))
    sd = pstdev(vals) if len(vals) > 1 else 0.0
    return max(0.0, 1.0 / (1.0 + avg + sd))


def inspect_file(path: Path, sample_count: int = 64) -> None:
    """Perform inspection and print results to logging."""
    logging.info("File: %s", path)
    size = path.stat().st_size
    logging.info("Size: %d bytes", size)
    with path.open("rb") as fh:
        data = fh.read()

    # ASCII runs
    ascii_runs = find_ascii_runs(data[:8192], min_len=6)
    if ascii_runs:
        logging.info("ASCII runs (sample):")
        for s in ascii_runs[:10]:
            logging.info("  %s", s)
    else:
        logging.info("No long ASCII runs found in first 8 KiB")

    # try float interpretations at several offsets
    logging.info("Float samples (offset, endian, score, first 8 values):")
    offsets = list(range(0, min(1024, len(data) - 4), max(4, min(64, len(data) // 16))))
    for off in offsets[:32]:
        for endian in ("<", ">"):
            vals = sample_floats(data, offset=off, count=sample_count, endian=endian)
            if not vals:
                continue
            sc = score_float_list(vals)
            logging.info("  off=%04d  %s  score=%.4f  %s", off, "LE" if endian == "<" else "BE", sc, vals[:8])


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect .jcs files and sample float tables.")
    parser.add_argument("path", type=Path, help="Path to .jcs file")
    parser.add_argument("--count", type=int, default=64, help="Number of floats to sample at each offset")
    args = parser.parse_args()
    if not args.path.exists():
        logging.error("File not found: %s", args.path)
        return 1
    inspect_file(args.path, sample_count=args.count)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
