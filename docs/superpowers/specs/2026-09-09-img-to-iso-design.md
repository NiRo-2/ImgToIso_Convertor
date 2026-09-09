# Img to ISO Convertor — Design

**Date:** 2026-09-09  
**Status:** Approved

## Goal

A public, MIT-licensed, cross-platform tool that takes one optical disk image path (`.img`) and writes a sibling `.iso` in the same directory after validating ISO9660. Wrappers install Python 3 when missing.

## Constraints

- Public repo: no secrets, private paths, credentials, or real disk dumps
- `LICENSE` is user-provided MIT — leave unchanged
- Python 3.9+ stdlib only (no pip dependencies)
- Windows, Linux, and macOS
- Validate ISO9660 then copy; do not rebuild raw HDD/USB dumps into ISOs
- Exactly one CLI argument: input path
- Output: same directory, same stem, `.iso` suffix
- Refuse to overwrite an existing output file
- Validate before and after copy (size + magic)

## Architecture

```
User → run.bat / run.sh → (ensure Python 3) → img_to_iso.py
         → ISO9660 check (CD001 at PVD offset)
         → copy to sibling .iso
         → re-validate size + magic
         → print path or exit non-zero
```

## Repo layout

| Path | Role |
|------|------|
| `img_to_iso.py` | CLI, validation, copy, post-check |
| `run.bat` | Windows wrapper + winget Python install |
| `run.sh` | Unix wrapper + brew/apt/dnf Python install |
| `tests/test_img_to_iso.py` | Stdlib unittest with synthetic fixtures |
| `README.md` / `.gitignore` | Public hygiene |
| `LICENSE` | Existing MIT (out of scope for edits) |

## CLI

```text
run.bat path\to\disk.img
./run.sh /path/to/disk.img
python img_to_iso.py /path/to/disk.img
```

## Validation

- Input must exist and be a regular file
- File must be large enough for sector 16 (≥ `16 * 2048 + 6` bytes)
- Bytes at offset `16 * 2048 + 1` must equal `CD001` (ISO9660 Primary Volume Descriptor standard identifier)
- After `shutil.copy2`: output exists, sizes match, magic still present

## Errors

Non-zero exit with plain stderr messages for:

- Wrong argument count
- Path missing / not a file
- Not ISO9660 (explain this tool only copies validated optical images)
- Output already exists
- Copy or post-check failure

## Out of scope

- Rebuilding ISOs from raw disk images
- GUI
- Overwrite flag
- Batch folder conversion
