# GTA6 iPhone / iOS Touch Port

## Current flow
BOOT -> full loading video -> main menu -> STORY MODE -> story video -> menu

All five original menu tabs are visible. STORY MODE is the only active tab; the other four are intentionally inactive placeholders for now.

The loading and story videos use a fixed 16:9 stage and are contained without stretching. The loading screen switches to the menu automatically at end-of-media. Story has no visible back button; double-tap anywhere on the story video returns to the menu.

### Windows test
Use Python 3.12 and:

`python -m pip install -r requirements-windows-test.txt`

then:

`python main_ios.py`

### iOS build
Use the existing `build_ios.sh` on macOS/Xcode.
