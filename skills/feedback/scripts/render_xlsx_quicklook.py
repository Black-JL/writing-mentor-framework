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
