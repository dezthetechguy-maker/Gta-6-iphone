#!/bin/sh
set -e

# Kivy-ios should be installed inside a virtual environment. macOS runners
# use an externally-managed Homebrew Python, so system-wide pip installs fail.
VENV_DIR="${VENV_DIR:-.venv}"
if [ ! -x "$VENV_DIR/bin/python" ]; then
    python3 -m venv "$VENV_DIR"
fi
. "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip setuptools wheel
python -m pip install --upgrade "Cython<3.4" packaging kivy-ios

# Build the Python + Kivy + video recipes used by the app.
# ffpyplayer provides the Kivy video backend used by main_ios.py.
toolchain build python3 kivy ffpyplayer

# Kivy-ios requires an app entry point named main.py.
toolchain create "GTA6_iPhone" . --alias gta6_ios
printf '\nXcode project created.\n'
