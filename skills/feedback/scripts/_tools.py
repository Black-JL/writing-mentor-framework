"""
Shared helpers for the feedback scripts: find command-line tools on macOS,
Linux and Windows, and run them with UTF-8 output.

On Windows, winget and the UB Mannheim installer often do not add poppler or
tesseract to PATH, so this module also looks in their usual install folders.
"""

import glob
import os
import shutil
import subprocess
import sys
from pathlib import Path

IS_WINDOWS = sys.platform.startswith('win')
IS_MAC = sys.platform == 'darwin'


def utf8_console():
    """Stop print() from crashing on symbols like ✓ when Windows output is piped."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors='replace')
        except (AttributeError, ValueError):
            pass


def _windows_candidates(name):
    """Usual Windows install folders for the tools this framework uses."""
    pf = os.environ.get('ProgramFiles', r'C:\Program Files')
    pf86 = os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)')
    local = os.environ.get('LOCALAPPDATA', '')
    home = str(Path.home())
    patterns = {
        'tesseract': [
            rf'{pf}\Tesseract-OCR\tesseract.exe',
            rf'{pf86}\Tesseract-OCR\tesseract.exe',
            rf'{local}\Programs\Tesseract-OCR\tesseract.exe',
        ],
        'pdftotext': [
            rf'{local}\Microsoft\WinGet\Packages\oschwartz10612.Poppler*\poppler-*\Library\bin\pdftotext.exe',
            rf'{pf}\poppler*\Library\bin\pdftotext.exe',
            rf'{pf}\poppler*\bin\pdftotext.exe',
            r'C:\ProgramData\chocolatey\lib\poppler\tools\*\bin\pdftotext.exe',
            rf'{home}\scoop\apps\poppler\current\Library\bin\pdftotext.exe',
            rf'{home}\scoop\apps\poppler\current\bin\pdftotext.exe',
        ],
        'soffice': [
            rf'{pf}\LibreOffice\program\soffice.exe',
            rf'{pf86}\LibreOffice\program\soffice.exe',
        ],
    }
    if name == 'pdftoppm':
        return [p.replace('pdftotext.exe', 'pdftoppm.exe') for p in patterns['pdftotext']]
    return patterns.get(name, [])


def find_tool(name):
    """Return the full path to a tool, or None if it is not installed."""
    found = shutil.which(name)
    if found:
        return found
    candidates = []
    if IS_WINDOWS:
        candidates = _windows_candidates(name)
    elif IS_MAC and name == 'soffice':
        candidates = ['/Applications/LibreOffice.app/Contents/MacOS/soffice']
    elif IS_MAC:
        candidates = [f'/opt/homebrew/bin/{name}', f'/usr/local/bin/{name}']
    for pattern in candidates:
        matches = sorted(glob.glob(pattern), reverse=True)  # newest version first
        if matches:
            return matches[0]
    return None


def tool(name):
    """Like find_tool, but raise a clear error when the tool is missing."""
    path = find_tool(name)
    if not path:
        raise FileNotFoundError(
            f"'{name}' was not found. Run check_dependencies.py for install steps."
        )
    return path


def run(cmd, check=True, env=None, timeout=300):
    """Run a command, read its output as UTF-8 (Windows defaults to cp1252), and give up
    after `timeout` seconds so a stuck program can't stall a review."""
    return subprocess.run(
        cmd, capture_output=True, text=True, encoding='utf-8', errors='replace',
        check=check, env=env, timeout=timeout,
    )


def pdf_to_pngs(pdf_path, out_prefix, dpi=200):
    """Turn each PDF page into a PNG with poppler's pdftoppm."""
    run([tool('pdftoppm'), '-r', str(dpi), '-png', str(pdf_path), str(out_prefix)])
