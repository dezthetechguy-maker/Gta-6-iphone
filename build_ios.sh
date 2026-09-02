#!/bin/sh
set -e
python3 -m pip install --upgrade pip setuptools wheel cython kivy-ios
# Build the Python + Kivy recipes used by the app.
toolchain build python3 kivy
# Create the Xcode project from this directory.
toolchain create "GTA6 iPhone" . --alias gta6_ios
printf '\nXcode project created. Open the generated .xcodeproj on macOS.\n'
