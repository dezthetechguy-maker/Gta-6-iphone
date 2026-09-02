#!/bin/sh
set -eu

# Build with a clean virtual environment on the GitHub macOS runner.
VENV_DIR="${VENV_DIR:-.venv}"
if [ ! -x "$VENV_DIR/bin/python" ]; then
    python3 -m venv "$VENV_DIR"
fi
. "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip setuptools wheel
# Pin the known stable kivy-ios release used for Xcode 16 support.
python -m pip install --upgrade "kivy-ios==2025.05.17" "Cython==0.29.37" packaging

# Build the Python + Kivy + FFmpeg video stack required by main_ios.py.
# ffpyplayer is required because the app explicitly selects the ffpyplayer
# Kivy video provider.
toolchain build python3 kivy ffpyplayer

# Kivy-ios requires an app entry point named main.py.
# The current toolchain create command accepts only NAME and DIRECTORY;
# --alias is not a valid create option.
rm -rf gta6_ios-ios
rm -rf GTA6_iPhone-ios
toolchain create GTA6_iPhone "$PWD"
printf '\nXcode project created successfully.\n'
