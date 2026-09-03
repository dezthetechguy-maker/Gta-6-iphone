#!/bin/sh
set -eu

# Kivy-ios creates <title>-ios inside the current working directory.
# Keep the application source that toolchain create() copies separate from
# the live checkout/toolchain build directory.  Kivy-ios builds FFmpeg and
# other recipes under ./build; that directory changes while Xcode's generated
# Run Script uses rsync, which can otherwise hit rsync exit 24 (files vanished).
APP_NAME="gta6_iphone"
APP_DIR="${APP_NAME}-ios"
TOOLCHAIN_DIR="${RUNNER_TEMP:-/tmp}/gta6-ios-toolchain"
SOURCE_DIR="${RUNNER_TEMP:-/tmp}/gta6-ios-source"

rm -rf "$TOOLCHAIN_DIR" "$SOURCE_DIR"
mkdir -p "$TOOLCHAIN_DIR" "$SOURCE_DIR"
python3 -m venv "$TOOLCHAIN_DIR/venv"
. "$TOOLCHAIN_DIR/venv/bin/activate"

python -m pip install --upgrade pip setuptools wheel
python -m pip install "kivy-ios==2025.5.17" "Cython==0.29.37" packaging

# Build the Python, Kivy, and FFmpeg/ffpyplayer recipes used by the app.
# Kivy-ios may create a large ./build tree in the checkout; it is deliberately
# NOT copied into the application source staged below.
toolchain build python3 kivy ffpyplayer

# The application source must contain main.py.  Stage only the files needed by
# the app so the generated Xcode project's rsync phase never sees the mutable
# Kivy-ios ./build tree or the generated <name>-ios project itself.
test -f "$PWD/main.py"

tar -cf - \
    --exclude='./.git' \
    --exclude='./.github' \
    --exclude='./build' \
    --exclude="./$APP_DIR" \
    --exclude='./dist' \
    --exclude='./__pycache__' \
    --exclude='*/__pycache__' \
    -C "$PWD" . | tar -xf - -C "$SOURCE_DIR"

# Keep the generated Xcode project in the checkout, but copy application data
# from the stable staging directory.
PROJECT_DIR="$PWD/$APP_DIR"
rm -rf "$PROJECT_DIR"
toolchain create "$APP_NAME" "$SOURCE_DIR"

# .xcodeproj is a directory, not a regular file.
PROJECT_FILE="$(find "$PROJECT_DIR" -maxdepth 1 -type d -name '*.xcodeproj' -print -quit)"

if [ -z "$PROJECT_FILE" ]; then
    echo "ERROR: kivy-ios did not create an Xcode project in $PROJECT_DIR" >&2
    find "$PWD" -maxdepth 2 -type d -name '*-ios' -print >&2 || true
    exit 1
fi

# Export paths for the GitHub Actions job.
echo "KIVY_IOS_PROJECT_DIR=$PROJECT_DIR" >> "$GITHUB_ENV"
echo "KIVY_IOS_PROJECT_FILE=$PROJECT_FILE" >> "$GITHUB_ENV"

echo "Created Xcode project: $PROJECT_FILE"
