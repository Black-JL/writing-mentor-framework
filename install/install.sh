#!/bin/bash
# Writing Mentor installer for macOS.
#   curl -fsSL https://raw.githubusercontent.com/Black-JL/writing-mentor-framework/main/install/install.sh | bash
# Installs what is missing (poppler, Tesseract, Python, Claude Code) with Homebrew,
# downloads the framework to ~/writing-mentor-framework, and adds the /mentor command.
# Safe to run again: it updates the framework and skips what is already installed.
#
# Optional settings (for testing):
#   WMF_SOURCE  copy the framework from this folder instead of downloading it
#   WMF_BRANCH  download this branch instead of main
set -euo pipefail

REPO="Black-JL/writing-mentor-framework"
BRANCH="${WMF_BRANCH:-main}"
TARGET="$HOME/writing-mentor-framework"

say()  { printf '%s\n' "$*"; }
step() { printf '\n== %s\n' "$*"; }
fail() { printf '\nSetup stopped: %s\n' "$*" >&2; exit 1; }

say ""
say "Writing Mentor setup"
say "--------------------"
say "This installs the programs the Writing Mentor needs (poppler for PDFs, Tesseract"
say "for scanned pages, Python, and Claude Code), puts the framework in $TARGET,"
say "and adds the /mentor command to Claude Code. Installed programs are left alone."

step "Checking for Homebrew"
for b in /opt/homebrew/bin/brew /usr/local/bin/brew; do
  [ -x "$b" ] && eval "$("$b" shellenv)" && break
done
command -v brew >/dev/null 2>&1 || fail "Homebrew is missing. Install it from https://brew.sh (it asks for your Mac password), then run this setup again."
say "  Found."

step "Installing programs"
for pkg in poppler tesseract; do
  if brew list --formula "$pkg" >/dev/null 2>&1; then
    say "  $pkg is already installed."
  else
    say "  Installing $pkg..."
    brew install --quiet "$pkg" || fail "$pkg could not be installed."
  fi
done

PYTHON=""
for p in "$(brew --prefix)/bin/python3" /usr/bin/python3; do
  if [ -x "$p" ] && "$p" -c 'import sys; sys.exit(sys.version_info < (3, 9))' >/dev/null 2>&1; then PYTHON="$p"; break; fi
done
if [ -z "$PYTHON" ]; then
  say "  Installing Python..."
  brew install --quiet python || fail "Python could not be installed."
  PYTHON="$(brew --prefix)/bin/python3"
else
  say "  Python is already installed."
fi

export PATH="$HOME/.local/bin:$PATH"
if command -v claude >/dev/null 2>&1; then
  say "  Claude Code is already installed."
else
  say "  Installing Claude Code..."
  curl -fsSL https://claude.ai/install.sh | bash || fail "Claude Code could not be installed. See https://code.claude.com/docs/en/setup"
fi

step "Getting the Writing Mentor framework"
STAGING="$(mktemp -d)"
trap 'rm -rf "$STAGING"' EXIT
if [ -n "${WMF_SOURCE:-}" ]; then
  say "  Copying from $WMF_SOURCE"
  SRC="$WMF_SOURCE"
else
  say "  Downloading from github.com/$REPO ($BRANCH)"
  curl -fsSL "https://github.com/$REPO/archive/refs/heads/$BRANCH.zip" -o "$STAGING/framework.zip" || fail "download failed."
  unzip -q "$STAGING/framework.zip" -d "$STAGING/x"
  SRC="$(find "$STAGING/x" -mindepth 1 -maxdepth 1 -type d | head -1)"
fi
if [ -d "$TARGET/.git" ]; then
  say "  $TARGET is a Git copy; leaving its files alone (update it with: git pull)."
else
  mkdir -p "$TARGET"
  find "$TARGET" -mindepth 1 -maxdepth 1 ! -name .venv -exec rm -rf {} +
  ( cd "$SRC" && find . -mindepth 1 -maxdepth 1 ! -name .git ! -name .venv ! -name .github -exec cp -R {} "$TARGET"/ \; )
  say "  Framework is in $TARGET"
fi

step "Setting up Python packages"
VPY="$TARGET/.venv/bin/python"
[ -x "$VPY" ] || "$PYTHON" -m venv "$TARGET/.venv" || fail "could not create the Python environment."
"$VPY" -m pip install --quiet --disable-pip-version-check --upgrade olefile python-docx || fail "could not install the Python packages."
say "  Done."

step "Adding the /mentor command to Claude Code"
SKILL_DIR="$HOME/.claude/skills/mentor"
mkdir -p "$SKILL_DIR"
"$VPY" - "$TARGET" "$VPY" "$SKILL_DIR/SKILL.md" <<'PY'
import sys
from pathlib import Path
target, vpy, out = sys.argv[1:4]
text = (Path(target) / 'skills' / 'mentor' / 'SKILL.md').read_text(encoding='utf-8')
Path(out).write_text(text.replace('{{FRAMEWORK}}', target).replace('{{PYTHON}}', vpy), encoding='utf-8')
PY
say "  Added: $SKILL_DIR/SKILL.md"

step "Checking everything"
set +e
"$VPY" "$TARGET/skills/feedback/scripts/check_dependencies.py"
CODE=$?
set -e

say ""
say "--------------------"
if [ $CODE -eq 0 ]; then say "Setup finished."; else say "Setup finished, but some items above are missing. Run setup again to retry."; fi
say ""
say "Next:"
say "  1. In Cursor, install the \"Claude Code\" extension (Extensions panel, search \"Claude Code\"),"
say "     or use the Code tab in the Claude desktop app."
say "  2. Open the folder that holds the writers' files."
say "  3. Open Claude Code, sign in with your Claude account if asked, and type:  /mentor"
say ""
say "To update later, run this setup again."
exit $CODE
