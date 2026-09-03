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
auto_project_dir="gta6_iphone-ios"
rm -rf "$auto_project_dir"
toolchain create GTA6_iPhone "$PWD"

# kivy-ios creates the Xcode project inside the application source directory.
# Its generated resource-copy phase rsyncs the whole source directory into
# YourApp. Exclude generated/build-only trees so Xcode cannot race with rsync
# and so the Python compile phase does not scan the toolchain itself.
# Do not quote the exclude values: the generated pbxproj is an old-style
# property list, so literal quotes here would corrupt its syntax.
PBXPROJ="$PWD/$auto_project_dir/gta6_iphone.xcodeproj/project.pbxproj"
python3 -c 'from pathlib import Path; import re; p=Path("'"$PBXPROJ"'"); s=p.read_text(); old="rsync -av --delete"; new="rsync -av --delete --exclude=gta6_iphone-ios --exclude=.git --exclude=.venv --exclude=xcode-build --exclude=diagnostics --exclude=build --exclude=dist"; assert old in s, "Generated Xcode rsync command not found"; s=s.replace(old, new, 1); pattern=r"/dist/hostpython3/bin/python -m compileall -f -b \"\$PROJECT_DIR\"/YourApp"; replacement="/dist/hostpython3/bin/python -m compileall -q \$PROJECT_DIR/YourApp/main.py \$PROJECT_DIR/YourApp/main_ios.py \$PROJECT_DIR/YourApp/desktop_main.py \$PROJECT_DIR/YourApp/ui \$PROJECT_DIR/YourApp/utils"; s,n=re.subn(pattern, replacement, s, count=1); assert n == 1, "Generated Xcode compileall command not found"; p.write_text(s)'

# Verify the generated project is still a valid OpenStep property list and
# that the two critical generated shell phases contain the intended commands.
python3 -c 'from pathlib import Path; p=Path("'"$PBXPROJ"'"); s=p.read_text(); assert "--exclude=build --exclude=dist" in s; assert "compileall -q $PROJECT_DIR/YourApp/main.py $PROJECT_DIR/YourApp/main_ios.py $PROJECT_DIR/YourApp/desktop_main.py $PROJECT_DIR/YourApp/ui $PROJECT_DIR/YourApp/utils" in s; print("Generated Xcode build phases verified.")'

printf '\nXcode project created and generated build phases patched successfully.\n'
