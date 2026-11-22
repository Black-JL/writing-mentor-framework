#!/usr/bin/env python3
"""Render XLSX to PNG with macOS Quick Look (macOS only; low chart fidelity)."""
import subprocess
import sys
from pathlib import Path


def render_xlsx(path, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        'qlmanage',
        '-t',
        '-s', '1400',
        '-o', str(out_dir),
        str(path)
    ], check=True, capture_output=True, text=True, timeout=90)  # Quick Look can hang with no screen


if __name__ == '__main__':
    # Older review folders call this script directly; hand off to render_charts.py,
    # which picks the best tool installed (same --input/--out options).
    import sys as _sys
    from render_charts import main as _main
    _sys.exit(_main())
