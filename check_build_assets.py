from pathlib import Path
import sys

base = Path(sys.executable).resolve().parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent
assets = base / 'assets'
print('Base:', base)
print('Assets:', assets)
for rel in ('icon.ico', 'videos/loading.mp4', 'videos/story.mp4'):
    p = assets / rel
    print(f'{rel}:', 'OK' if p.exists() else 'MISSING', str(p))
