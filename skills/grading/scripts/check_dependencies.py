#!/usr/bin/env python3
"""
Check for required dependencies and report what's missing.
Returns exit code 0 if all dependencies are present, 1 if any are missing.
"""

import subprocess
import sys
import shutil


def check_python_package(package_name):
    """Check if a Python package is installed."""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False


def check_command(command):
    """Check if a command-line tool is available."""
    return shutil.which(command) is not None


def main():
    missing = []
    install_commands = []

    # Check Python packages
    if not check_python_package('olefile'):
        missing.append('olefile (Python package)')
        install_commands.append('pip install olefile')

    # Check command-line tools
    if not check_command('pdftotext'):
        missing.append('poppler (provides pdftotext for PDF extraction)')
        install_commands.append('brew install poppler')

    if not check_command('tesseract'):
        missing.append('tesseract (OCR for scanned PDFs)')
        install_commands.append('brew install tesseract')

    if not missing:
        print("✓ All dependencies are installed.")
        return 0

    print("Missing dependencies:\n")
    for item in missing:
        print(f"  ✗ {item}")

    print("\nInstall commands:\n")
    for cmd in install_commands:
        print(f"  {cmd}")

    print("\nRun these commands to install missing dependencies.")
    return 1


if __name__ == '__main__':
    sys.exit(main())
