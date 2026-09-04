#!/bin/sh
set -eu

# Kivy-ios creates <title>-ios inside the current working directory.
# Keep the application source that toolchain create() copies separate from
# the live checkout/toolchain build directory. Kivy-ios builds FFmpeg and
# other recipes under ./build; that directory changes while Xcode's generated
# Run Script uses rsync, which can otherwise hit rsync exit 24 (files vanished).
APP_NAME="gta6_iphone"
APP_DISPLAY_NAME="GTA 6 Dev Build"
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

# The application source must contain main.py. Stage only the files needed by
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

# Build a high-resolution square GTA VI source image from the supplied branding
# source available online, then use kivy-ios to generate the complete Xcode
# icon set. The square canvas also avoids the stretched/non-square icon failure
# mode of the old low-resolution asset.
ICON_WORK_DIR="${RUNNER_TEMP:-/tmp}/gta6-icon"
mkdir -p "$ICON_WORK_DIR"
ICON_SVG="$ICON_WORK_DIR/gta6-logo.svg"
ICON_RECT="$ICON_WORK_DIR/gta6-logo-rect.png"
ICON_FILE="$ICON_WORK_DIR/gta6-icon-1024.png"

curl -fsSL \
  'https://upload.wikimedia.org/wikipedia/commons/d/d6/Grand_Theft_Auto_VI_logo_%28with_gradient%29.svg' \
  -o "$ICON_SVG"

# The source artwork is landscape. Rasterize it large, then center it on an
# opaque 1024x1024 black canvas so it remains visually intact as an iOS icon.
rsvg-convert -w 1000 -h 760 "$ICON_SVG" -o "$ICON_RECT"
python3 - "$ICON_RECT" "$ICON_FILE" <<'PY'
from PIL import Image
import sys

src = Image.open(sys.argv[1]).convert('RGBA')
out = Image.new('RGBA', (1024, 1024), (0, 0, 0, 255))
src.thumbnail((1000, 760), Image.Resampling.LANCZOS)
x = (1024 - src.width) // 2
y = (1024 - src.height) // 2
out.alpha_composite(src, (x, y))
out.convert('RGB').save(sys.argv[2], 'PNG', optimize=True)
PY

test -s "$ICON_FILE"
toolchain icon "$PROJECT_DIR" "$ICON_FILE"

test -f "$ICON_FILE"
echo "Configured application icon from high-resolution GTA VI artwork: $ICON_FILE"

# Kivy's default launch image is the Kivy logo. Generate GTA VI launch images
# so startup does not show the Kivy branding. Kivy-ios documents the
# launchimage command for registering the project's launch artwork.
toolchain launchimage "$PROJECT_DIR" "$ICON_FILE"
echo "Configured GTA VI launch image: $ICON_FILE"

# Kivy-ios commonly names the generated plist <app>-Info.plist rather than
# Info.plist. Locate either form so orientation and display-name configuration
# works across Kivy-ios/Xcode project layouts.
PLIST_FILE="$(find "$PROJECT_DIR" -type f \( -name 'Info.plist' -o -name '*-Info.plist' \) -print -quit)"
if [ -z "$PLIST_FILE" ]; then
    echo "ERROR: Generated Xcode project does not contain an application Info.plist." >&2
    find "$PROJECT_DIR" -maxdepth 6 -type f -name '*.plist' -print >&2 || true
    exit 1
fi

/usr/libexec/PlistBuddy -c 'Delete :UISupportedInterfaceOrientations' "$PLIST_FILE" 2>/dev/null || true
/usr/libexec/PlistBuddy -c 'Add :UISupportedInterfaceOrientations array' "$PLIST_FILE"
/usr/libexec/PlistBuddy -c 'Add :UISupportedInterfaceOrientations: string UIInterfaceOrientationLandscapeLeft' "$PLIST_FILE"
/usr/libexec/PlistBuddy -c 'Add :UISupportedInterfaceOrientations: string UIInterfaceOrientationLandscapeRight' "$PLIST_FILE"
/usr/libexec/PlistBuddy -c 'Delete :UIRequiresFullScreen' "$PLIST_FILE" 2>/dev/null || true
/usr/libexec/PlistBuddy -c 'Add :UIRequiresFullScreen bool true' "$PLIST_FILE"

# Set the user-visible iOS application name. The filesystem/Xcode target keeps
# its stable internal name gta6_iphone, while the Home Screen/app switcher name
# becomes GTA 6 Dev Build.
/usr/libexec/PlistBuddy -c 'Delete :CFBundleDisplayName' "$PLIST_FILE" 2>/dev/null || true
/usr/libexec/PlistBuddy -c "Add :CFBundleDisplayName string $APP_DISPLAY_NAME" "$PLIST_FILE"
/usr/libexec/PlistBuddy -c 'Delete :CFBundleName' "$PLIST_FILE" 2>/dev/null || true
/usr/libexec/PlistBuddy -c "Add :CFBundleName string $APP_DISPLAY_NAME" "$PLIST_FILE"

echo "Configured landscape-only iOS orientation in: $PLIST_FILE"
echo "Configured display name: $APP_DISPLAY_NAME"

# Export paths for the GitHub Actions job.
echo "KIVY_IOS_PROJECT_DIR=$PROJECT_DIR" >> "$GITHUB_ENV"
echo "KIVY_IOS_PROJECT_FILE=$PROJECT_FILE" >> "$GITHUB_ENV"

echo "Created Xcode project: $PROJECT_FILE"
