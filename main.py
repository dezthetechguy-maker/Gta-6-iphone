import sys

# Kivy-ios requires the application's entry point to be named main.py.
# Keep the existing Windows/PySide6 app available on desktop while using the
# Kivy implementation when this same source tree is packaged for iOS.
if sys.platform == 'ios':
    from main_ios import GTA6iOS

    GTA6iOS().run()
else:
    from desktop_main import main

    if __name__ == '__main__':
        main()
