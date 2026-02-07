#!/usr/bin/env python3
"""
Check for required dependencies and provide platform-specific install guidance.
Returns exit code 0 if all dependencies are present, 1 if any are missing.
"""

import subprocess
import sys
import shutil
import platform


def get_platform_info():
    """Detect OS and available package managers."""
    system = platform.system().lower()

    package_managers = {
        'brew': shutil.which('brew'),
        'apt': shutil.which('apt-get'),
        'dnf': shutil.which('dnf'),
        'yum': shutil.which('yum'),
        'pacman': shutil.which('pacman'),
        'choco': shutil.which('choco'),
        'winget': shutil.which('winget'),
        'scoop': shutil.which('scoop'),
    }

    available_managers = [k for k, v in package_managers.items() if v]

    return system, available_managers


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


def get_install_instructions(system, managers):
    """Get platform-specific install instructions."""

    instructions = {
        'olefile': {
            'description': 'Python package for reading older Office file formats',
            'all_platforms': 'pip install olefile',
        },
        'poppler': {
            'description': 'PDF toolkit (provides pdftotext for extracting text from PDFs)',
            'darwin': {
                'brew': 'brew install poppler',
            },
            'linux': {
                'apt': 'sudo apt-get install poppler-utils',
                'dnf': 'sudo dnf install poppler-utils',
                'yum': 'sudo yum install poppler-utils',
                'pacman': 'sudo pacman -S poppler',
            },
            'windows': {
                'choco': 'choco install poppler',
                'scoop': 'scoop install poppler',
                'manual': 'Download from: https://github.com/oschwartz10612/poppler-windows/releases',
            },
        },
        'tesseract': {
            'description': 'OCR engine for extracting text from scanned/image-based PDFs',
            'darwin': {
                'brew': 'brew install tesseract',
            },
            'linux': {
                'apt': 'sudo apt-get install tesseract-ocr',
                'dnf': 'sudo dnf install tesseract',
                'yum': 'sudo yum install tesseract',
                'pacman': 'sudo pacman -S tesseract',
            },
            'windows': {
                'choco': 'choco install tesseract',
                'scoop': 'scoop install tesseract',
                'manual': 'Download from: https://github.com/UB-Mannheim/tesseract/wiki',
            },
        },
    }

    return instructions


def get_package_manager_install_instructions(system, managers):
    """Get instructions for installing a package manager if none available."""

    if system == 'darwin':
        return {
            'name': 'Homebrew',
            'description': 'The most common package manager for macOS',
            'install': '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
            'url': 'https://brew.sh',
        }
    elif system == 'windows':
        return {
            'name': 'Chocolatey or Scoop',
            'description': 'Popular package managers for Windows',
            'chocolatey': {
                'install': 'Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString("https://community.chocolatey.org/install.ps1"))',
                'url': 'https://chocolatey.org/install',
            },
            'scoop': {
                'install': 'irm get.scoop.sh | iex',
                'url': 'https://scoop.sh',
            },
        }
    elif system == 'linux':
        return {
            'name': 'System package manager',
            'description': 'Most Linux distributions come with a package manager (apt, dnf, pacman, etc.)',
            'note': 'Your distribution should have a package manager pre-installed.',
        }

    return None


def main():
    system, managers = get_platform_info()
    instructions = get_install_instructions(system, managers)

    # Track what's missing
    missing = []

    # Check Python packages
    if not check_python_package('olefile'):
        missing.append('olefile')

    # Check command-line tools
    if not check_command('pdftotext'):
        missing.append('poppler')

    if not check_command('tesseract'):
        missing.append('tesseract')

    # All good!
    if not missing:
        print("✓ All dependencies are installed. The framework is ready to use.")
        return 0

    # Report what's missing
    print("=" * 70)
    print("WRITING MENTOR FRAMEWORK — DEPENDENCY CHECK")
    print("=" * 70)
    print()
    print("Some dependencies are missing. These are optional but recommended")
    print("for full functionality:")
    print()

    for pkg in missing:
        info = instructions[pkg]
        print(f"  ✗ {pkg}")
        print(f"    {info['description']}")
        print()

    print("-" * 70)
    print("WHAT HAPPENS WITHOUT THESE?")
    print("-" * 70)
    print()
    if 'olefile' in missing:
        print("  • Without olefile: Cannot read older .doc/.xls formats (pre-2007)")
    if 'poppler' in missing:
        print("  • Without poppler: Cannot extract text from PDF files")
    if 'tesseract' in missing:
        print("  • Without tesseract: Cannot OCR scanned/image-based PDFs")
    print()
    print("The framework will still work for supported file types.")
    print()

    print("-" * 70)
    print("HOW TO INSTALL")
    print("-" * 70)
    print()

    # Check if we need a package manager first
    need_pkg_manager = ('poppler' in missing or 'tesseract' in missing) and not managers

    if need_pkg_manager:
        pm_info = get_package_manager_install_instructions(system, managers)
        if pm_info:
            print(f"First, you'll need a package manager ({pm_info['name']}):")
            print()
            if system == 'darwin':
                print(f"  {pm_info['install']}")
                print(f"  More info: {pm_info['url']}")
            elif system == 'windows':
                print("  Option 1 - Chocolatey (run in admin PowerShell):")
                print(f"    {pm_info['chocolatey']['url']}")
                print()
                print("  Option 2 - Scoop (run in PowerShell):")
                print(f"    {pm_info['scoop']['install']}")
                print(f"    More info: {pm_info['scoop']['url']}")
            print()
            print("After installing a package manager, run this check again.")
            print()

    # Show install commands for missing packages
    print("Install commands for your system:")
    print()

    for pkg in missing:
        info = instructions[pkg]
        print(f"  {pkg}:")

        if 'all_platforms' in info:
            print(f"    {info['all_platforms']}")
        elif system in info:
            platform_info = info[system]
            shown = False
            for mgr in managers:
                if mgr in platform_info:
                    print(f"    {platform_info[mgr]}")
                    shown = True
                    break
            if not shown and 'manual' in platform_info:
                print(f"    {platform_info['manual']}")
        print()

    print("-" * 70)
    print("IT'S UP TO YOU")
    print("-" * 70)
    print()
    print("Installing these dependencies is your choice. The framework will")
    print("prompt you before running any install commands, and you can always")
    print("install them manually using the commands above.")
    print()
    print("Run this check again after installing to verify:")
    print("  python skills/feedback/scripts/check_dependencies.py")
    print()

    return 1


if __name__ == '__main__':
    sys.exit(main())
