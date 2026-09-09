#!/usr/bin/env python3
"""Convert a validated optical .img (ISO9660) to a sibling .iso file."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Optional, Sequence

ISO_SECTOR_SIZE = 2048
ISO_PVD_OFFSET = 16 * ISO_SECTOR_SIZE + 1  # standard identifier "CD001"
ISO_MAGIC = b"CD001"


class ConvertError(Exception):
    """Raised when conversion cannot proceed or verification fails."""


def is_iso9660(path: Path) -> bool:
    """Return True if path contains ISO9660 Primary Volume Descriptor magic."""
    try:
        size = path.stat().st_size
    except OSError:
        return False
    if size < ISO_PVD_OFFSET + len(ISO_MAGIC):
        return False
    try:
        with path.open("rb") as fh:
            fh.seek(ISO_PVD_OFFSET)
            return fh.read(len(ISO_MAGIC)) == ISO_MAGIC
    except OSError:
        return False


def convert_img_to_iso(input_path: Path) -> Path:
    """
    Validate input as ISO9660, copy to sibling .iso, verify result.

    Returns the output path. Raises ConvertError on failure.
    """
    src = input_path.expanduser().resolve()
    if not src.exists():
        raise ConvertError(f"Input not found: {src}")
    if not src.is_file():
        raise ConvertError(f"Input is not a file: {src}")

    dest = src.with_suffix(".iso")
    if dest.exists():
        raise ConvertError(f"Output already exists (refusing to overwrite): {dest}")

    if not is_iso9660(src):
        raise ConvertError(
            "Input is not a valid ISO9660 optical image (missing CD001 at the "
            "Primary Volume Descriptor). This tool only copies validated optical "
            "images to .iso; it does not rebuild raw disk dumps."
        )

    try:
        shutil.copy2(src, dest)
    except OSError as exc:
        raise ConvertError(f"Copy failed: {exc}") from exc

    if not dest.is_file():
        raise ConvertError(f"Post-check failed: output missing after copy: {dest}")

    src_size = src.stat().st_size
    dest_size = dest.stat().st_size
    if dest_size != src_size:
        dest.unlink(missing_ok=True)
        raise ConvertError(
            f"Post-check failed: size mismatch (input {src_size}, output {dest_size})"
        )

    if not is_iso9660(dest):
        dest.unlink(missing_ok=True)
        raise ConvertError("Post-check failed: output is missing ISO9660 magic")

    return dest


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate an optical .img as ISO9660 and copy it to a sibling .iso "
            "in the same directory."
        )
    )
    parser.add_argument(
        "input_path",
        help="Path to the input .img (or other optical image file)",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        out = convert_img_to_iso(Path(args.input_path))
    except ConvertError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
