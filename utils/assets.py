from pathlib import Path
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

IMAGE_SUFFIXES = ('.png', '.jpg', '.jpeg', '.webp', '.bmp')
# Prefer common web-friendly formats when more than one file with the same
# stem exists. The fallback remains deterministic.
_SUFFIX_PRIORITY = {'.png': 0, '.jpg': 1, '.jpeg': 2, '.webp': 3, '.bmp': 4}


def files_in(directory: Path, suffixes=IMAGE_SUFFIXES):
    if not directory.exists():
        return []
    return [p for p in directory.iterdir() if p.is_file() and p.suffix.lower() in suffixes]


def find_first(directory: Path, suffixes=IMAGE_SUFFIXES):
    files = files_in(directory, suffixes)
    return min(files, key=lambda p: (_SUFFIX_PRIORITY.get(p.suffix.lower(), 99), p.name.lower()), default=None)


def find_named(directory: Path, names, suffixes=IMAGE_SUFFIXES):
    if not directory.exists():
        return None
    wanted = {n.lower().rsplit('.', 1)[0] for n in names}
    matches = [p for p in files_in(directory, suffixes) if p.stem.lower() in wanted]
    return min(matches, key=lambda p: (_SUFFIX_PRIORITY.get(p.suffix.lower(), 99), p.name.lower()), default=None)


def find_tab_image(tab_name: str, role: str):
    """Find a tab asset by role, accepting png/jpg/jpeg/webp/bmp."""
    base = Path(__file__).resolve().parents[1] / 'assets' / 'tabs' / tab_name.lower()
    return find_named(base, [role])


def find_tab_preview(tab_name: str):
    """Find the main-menu preview image named after the tab."""
    return find_tab_image(tab_name, tab_name.lower())


def find_tab_background(tab_name: str):
    """Find the background used after opening a tab."""
    return find_tab_image(tab_name, 'background')


def load_pixmap(path: Path | None, size):
    if path and path.exists():
        pm = QPixmap(str(path))
        if not pm.isNull():
            return pm.scaled(size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
    return None


def load_image(rel_path, fallback_color="#2a2a3a", fallback_text="Image not found"):
    """Load an asset relative to assets/, preserving legacy callers."""
    from PySide6.QtGui import QImage
    from PIL import Image, ImageDraw, ImageFont
    parts = rel_path.replace('\\', '/').split('/')
    path = Path(__file__).resolve().parents[1] / 'assets' / Path(*parts)
    if path.exists():
        return QPixmap(str(path))
    try:
        img = Image.new('RGB', (800, 600), color=fallback_color)
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype('arial.ttf', 36)
        except Exception:
            font = ImageFont.load_default()
        draw.text((400, 300), fallback_text, fill='white', anchor='mm', font=font)
        import io
        buf = io.BytesIO(); img.save(buf, format='PNG')
        return QPixmap.fromImage(QImage.fromData(buf.getvalue()))
    except Exception:
        return QPixmap()
