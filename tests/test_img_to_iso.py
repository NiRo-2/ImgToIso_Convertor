"""Tests for img_to_iso (synthetic ISO9660 fixtures only)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import img_to_iso
from img_to_iso import ConvertError, ISO_PVD_OFFSET, convert_img_to_iso, is_iso9660, main


def _write_bytes(path: Path, size: int, magic_at: int | None = ISO_PVD_OFFSET) -> None:
    data = bytearray(size)
    if magic_at is not None and magic_at + 5 <= size:
        data[magic_at : magic_at + 5] = b"CD001"
    path.write_bytes(data)


class IsIso9660Tests(unittest.TestCase):
    def test_detects_valid_magic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ok.img"
            _write_bytes(path, ISO_PVD_OFFSET + 5)
            self.assertTrue(is_iso9660(path))

    def test_rejects_missing_magic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.img"
            _write_bytes(path, ISO_PVD_OFFSET + 5, magic_at=None)
            self.assertFalse(is_iso9660(path))

    def test_rejects_too_small(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tiny.img"
            path.write_bytes(b"CD001")
            self.assertFalse(is_iso9660(path))


class ConvertTests(unittest.TestCase):
    def test_valid_creates_sibling_iso_same_size(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "disk.img"
            _write_bytes(src, ISO_PVD_OFFSET + 64)
            out = convert_img_to_iso(src)
            self.assertEqual(out, Path(tmp) / "disk.iso")
            self.assertTrue(out.is_file())
            self.assertEqual(out.stat().st_size, src.stat().st_size)
            self.assertTrue(is_iso9660(out))

    def test_missing_magic_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "disk.img"
            _write_bytes(src, ISO_PVD_OFFSET + 64, magic_at=None)
            with self.assertRaises(ConvertError):
                convert_img_to_iso(src)
            self.assertFalse((Path(tmp) / "disk.iso").exists())

    def test_missing_input_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "missing.img"
            with self.assertRaises(ConvertError):
                convert_img_to_iso(src)

    def test_output_exists_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "disk.img"
            existing = Path(tmp) / "disk.iso"
            _write_bytes(src, ISO_PVD_OFFSET + 64)
            existing.write_bytes(b"already here")
            with self.assertRaises(ConvertError) as ctx:
                convert_img_to_iso(src)
            self.assertIn("already exists", str(ctx.exception).lower())
            self.assertEqual(existing.read_bytes(), b"already here")


class MainTests(unittest.TestCase):
    def test_main_success_returns_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "disk.img"
            _write_bytes(src, ISO_PVD_OFFSET + 32)
            code = main([str(src)])
            self.assertEqual(code, 0)
            self.assertTrue((Path(tmp) / "disk.iso").is_file())

    def test_main_failure_returns_nonzero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "disk.img"
            _write_bytes(src, ISO_PVD_OFFSET + 32, magic_at=None)
            code = main([str(src)])
            self.assertNotEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
