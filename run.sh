#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY_SCRIPT="${SCRIPT_DIR}/img_to_iso.py"

have_python() {
  command -v python3 >/dev/null 2>&1
}

install_python() {
  echo "Python 3 not found. Attempting install..." >&2

  if [[ "$(uname -s)" == "Darwin" ]]; then
    if command -v brew >/dev/null 2>&1; then
      brew install python
      return
    fi
    echo "Error: Homebrew not found. Install Python 3 from https://www.python.org/downloads/ or install Homebrew, then re-run." >&2
    exit 1
  fi

  if command -v apt-get >/dev/null 2>&1; then
    if command -v sudo >/dev/null 2>&1; then
      sudo apt-get update
      sudo apt-get install -y python3
      return
    fi
    echo "Error: need sudo to install python3 via apt-get." >&2
    exit 1
  fi

  if command -v dnf >/dev/null 2>&1; then
    if command -v sudo >/dev/null 2>&1; then
      sudo dnf install -y python3
      return
    fi
    echo "Error: need sudo to install python3 via dnf." >&2
    exit 1
  fi

  echo "Error: no supported package manager found. Install Python 3 manually, then re-run." >&2
  exit 1
}

if ! have_python; then
  install_python
fi

if ! have_python; then
  echo "Error: Python 3 still not available after install attempt." >&2
  exit 1
fi

exec python3 "$PY_SCRIPT" "$@"
