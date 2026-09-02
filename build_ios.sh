#!/bin/sh
set -e

python3 -m pip install --upgrade pip setuptools wheel cython kivy-ios

# Video support: build Kivy together with the ffpyplayer/FFmpeg recipes.
toolchain build python3 kivy ffmpeg ffpyplayer

toolchain create "GTA6 iPhone" . --alias gta6_ios

printf '\nXcode project created in the generated build directory.\n'
