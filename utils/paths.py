import os
import sys


def get_base_path():
    """Return the directory containing the app assets.

    Works when running from source, PyInstaller onedir, and PyInstaller onefile.
    For onedir builds, assets are placed beside the executable. For onefile builds,
    PyInstaller extracts bundled data under sys._MEIPASS.
    """
    if getattr(sys, 'frozen', False):
        exe_base = os.path.dirname(os.path.abspath(sys.executable))
        if os.path.isdir(os.path.join(exe_base, 'assets')):
            return exe_base
        meipass = getattr(sys, '_MEIPASS', None)
        if meipass:
            return meipass
        return exe_base
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_asset_path(relative_path=''):
    """Return an absolute path to an item inside the packaged/source assets folder."""
    return os.path.join(get_base_path(), 'assets', relative_path)


def get_image_path(folder, filename):
    return os.path.join(get_asset_path(folder), filename)


def get_audio_path(filename):
    return os.path.join(get_asset_path('audio'), filename)
