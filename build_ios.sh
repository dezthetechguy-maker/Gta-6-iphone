#!/bin/sh
set -eu

# Kivy-ios creates <title>-ios next to the application directory.
# Keep all toolchain state outside the checkout so Xcode never syncs the
# virtual environment or generated build output into YourApp.
APP_NAME="gta6_iphone"
APP_DIR="${APP_NAME}-ios"
TOOLCHAIN_DIR="${RUNNER_TEMP:-/tmp}/gta6-ios-toolchain"

rm -rf "$TOOLCHAIN_DIR"
mkdir -p "$TOOLCHAIN_DIR"
python3 -m venv "$TOOLCHAIN_DIR/venv"
. "$TOOLCHAIN_DIR/venv/bin/activate"

python -m pip install --upgrade pip setuptools wheel
python -m pip install "kivy-ios==2025.5.17" "Cython==0.29.37" packaging

# Build the Python, Kivy, and FFmpeg/ffpyplayer recipes used by the app.
toolchain build python3 kivy ffpyplayer

# The app directory must be a fully-qualified path and must contain main.py.
test -f "$PWD/main.py"

# Kivy-ios creates gta6_iphone-ios beside the source checkout.
rm -rf "$(cd "$PWD/.." && pwd)/$APP_DIR"
toolchain create "$APP_NAME" "$PWD"

PROJECT_DIR="$(cd "$PWD/.." && pwd)/$APP_DIR"
PROJECT_FILE="$(find "$PROJECT_DIR" -maxdepth 1 -type f -name '*.xcodeproj' -print -quit)"

if [ -z "$PROJECT_FILE" ]; then
    echo "ERROR: kivy-ios did not create an Xcode project in $PROJECT_DIR" >&2
    find "$(cd "$PWD/.." && pwd)" -maxdepth 2 -type d -name '*-ios' -print >&2 || true
    exit 1
fi

# Export paths for the GitHub Actions job.
echo "KIVY_IOS_PROJECT_DIR=$PROJECT_DIR" >> "$GITHUB_ENV"
echo "KIVY_IOS_PROJECT_FILE=$PROJECT_FILE" >> "$GITHUB_ENV"

echo "Created Xcode project: $PROJECT_FILE"
