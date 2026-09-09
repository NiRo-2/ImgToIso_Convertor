# Img to ISO Convertor

Simple cross-platform tool: give it an optical `.img` path, get a sibling `.iso` in the same folder.

It checks that the file looks like ISO9660 (`CD001` at the standard Primary Volume Descriptor offset), copies it to `.iso`, then checks size and magic again. It does **not** rebuild raw hard-disk or USB dumps into ISOs.

## Requirements

- Python 3.9+ (stdlib only — no pip packages)
- `run.bat` / `run.sh` try to install Python 3 automatically if it is missing (`winget` on Windows; `brew` / `apt` / `dnf` on Unix)

## Usage

**Windows**

```bat
run.bat path\to\disk.img
```

**Linux / macOS**

```bash
chmod +x run.sh   # once
./run.sh /path/to/disk.img
```

**Direct Python**

```bash
python img_to_iso.py /path/to/disk.img
```

Output is written next to the input as `disk.iso`. If that file already exists, the tool exits without overwriting.

## Exit behavior

- `0` — conversion succeeded; output path is printed
- Non-zero — missing/invalid args, file not found, not ISO9660, output exists, or post-copy validation failed (message on stderr)

## Tests

```bash
python -m unittest tests.test_img_to_iso -v
```

## License

MIT — see [LICENSE](LICENSE).
