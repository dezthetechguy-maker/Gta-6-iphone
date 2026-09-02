# GTA VI Fan Dev Build — Combined Edition

This is a fan-made local mockup combining the two supplied builds.

## What was combined
- Cinematic image loading screen and artwork from **GTA6_FanDevBuild (2)(1)**.
- Large image-backed tab menu from **GTA6_FanDevBuild (2)**, redesigned as five large console-style tabs.
- **Free Roam removed** from the main menu.
- Menu buttons are wired to real screens: Story, Characters, Map, Options, Developer, and Exit.
- Story opens the supplied local `assets/videos/story.mp4` when available.
- Character and map screens use the supplied WEBP artwork.
- Developer tools route to build information, console, and build pipeline; previously inert developer actions now fall back to build information.

## Run
```bat
py -m pip install -r requirements.txt
py main.py
```

## Package
Run `build_exe.bat` on a machine with PyInstaller installed.

## Controls
- **F11** — fullscreen/windowed
- **Esc** — back to menu / exit from the menu
- **Space** — pause/resume story video

## Disclaimer
This is a FAN-MADE MOCKUP and is not affiliated with Rockstar Games.

## Customizing the build

### Loading video
Replace:
`assets/videos/loading.mp4`

The game plays this video during startup and goes to the main menu when the video ends.

### Menu pictures
Replace these files while keeping the same filenames:
- `assets/backgrounds/menu.jpg` — menu background / fallback tab artwork
- `assets/characters/lucia.webp` — Lucia artwork
- `assets/characters/jason.webp` — Jason artwork
- `assets/ui/map.webp` — map artwork

The menu tab image assignments are in `ui/main_menu.py` inside the `tabs = [...]` list.

### Options screen
Edit `ui/settings.py`. Add/remove controls there, and connect buttons/check boxes to real application settings as needed. The current controls are the display, graphics, and audio placeholders.

### Developer menu
Edit `ui/developer_menu.py` to change the developer buttons. The actions behind them are routed in `main.py` (`dev_action`). Existing screens include build information, console, and build pipeline.

### Map movement
`ui/map_screen.py` contains the map zoom and pan settings. `self._pan_speed = 0.33` controls panning speed; lower values make it slower. Wheel zoom uses 10% steps and supports 0.70x to 3.20x zoom.

## Program icon
The project includes `assets/icon.ico`, used by the app window and PyInstaller build. To change it, replace that file with another `.ico` file and rebuild the executable with `build_exe.bat`.
