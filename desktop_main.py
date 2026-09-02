import os
import sys
import time

from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget

from config import DISCORD_CLIENT_ID
from ui.boot_sequence import BootSequence
from ui.loading_screen import LoadingScreen
from ui.main_menu import MainMenu
from ui.character_select import CharacterSelect
from ui.map_screen import MapScreen
from ui.developer_menu import DeveloperMenu
from ui.dev_console import DevConsole
from ui.build_pipeline import BuildPipeline
from ui.build_info import BuildInfo
from ui.settings import SettingsScreen
from ui.video_screen import VideoScreen
from utils.paths import get_asset_path

try:
    from pypresence import Presence
    RPC_AVAILABLE = True
except ImportError:
    RPC_AVAILABLE = False


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Grand Theft Auto VI Development Build')
        self.setMinimumSize(1100, 650)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()

        icon = os.path.join(get_asset_path(''), 'icon.ico')
        if os.path.exists(icon):
            self.setWindowIcon(QIcon(icon))

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.rpc = self.init_rpc()
        self.build_pages()
        self.stack.setCurrentWidget(self.boot)
        self.loading.finished.connect(self.show_menu)
        self.boot_finished_called = False

    def init_rpc(self):
        if not RPC_AVAILABLE:
            return None
        try:
            rpc = Presence(DISCORD_CLIENT_ID)
            rpc.connect()
            rpc.update(details='Vice City Development Build', state='Booting', start=time.time())
            return rpc
        except Exception:
            return None

    def presence(self, details, state):
        if self.rpc:
            try:
                self.rpc.update(details=details, state=state, start=time.time())
            except Exception:
                pass

    def add(self, widget):
        self.stack.addWidget(widget)
        return widget

    def build_pages(self):
        self.boot = self.add(BootSequence(self.start_loading))
        self.loading = self.add(LoadingScreen())
        self.menu = self.add(MainMenu())
        self.char = self.add(CharacterSelect(self.show_menu))
        self.map = self.add(MapScreen(self.show_menu))
        self.settings = self.add(SettingsScreen(self.show_menu))
        self.dev = self.add(DeveloperMenu(self.dev_action, self.show_menu))
        self.console = self.add(DevConsole(self.show_dev))
        self.pipeline = self.add(BuildPipeline(self.show_dev))
        self.info = self.add(BuildInfo(self.show_dev))
        self.video = self.add(VideoScreen())

        self.menu.set_navigate_callback(self.route)
        self.video.finished.connect(self.show_menu)

    def transition_to(self, widget):
        old = self.stack.currentWidget()
        if old is widget:
            return
        if old:
            effect = old.graphicsEffect()
            if effect:
                old.setGraphicsEffect(None)
        self.stack.setCurrentWidget(widget)
        effect = widget.graphicsEffect()
        from PySide6.QtWidgets import QGraphicsOpacityEffect
        if effect is None:
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
        effect.setOpacity(0.0)
        anim = QPropertyAnimation(effect, b'opacity', widget)
        anim.setDuration(350)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        widget._fade_anim = anim
        anim.start()

    def start_loading(self):
        if self.boot_finished_called:
            return
        self.boot_finished_called = True
        self.presence('Loading Assets', 'Cinematic Loading Screen')
        self.transition_to(self.loading)
        self.loading.restart()

    def show_menu(self):
        self.presence('In Main Menu', 'Ready')
        self.transition_to(self.menu)

    def show_dev(self):
        self.presence('Developer Tools', 'Debugging Build')
        self.transition_to(self.dev)

    def route(self, item):
        if item == 'EXIT':
            if self.rpc:
                try: self.rpc.close()
                except Exception: pass
            self.close()
            return

        targets = {
            'CHARACTERS': self.char,
            'MAP': self.map,
            'OPTIONS': self.settings,
            'DEVELOPER': self.dev,
        }
        if item in targets:
            self.presence(item.title(), 'Vice City Development Build')
            self.transition_to(targets[item])
            return

        if item == 'STORY':
            video_path = os.path.join(get_asset_path('videos'), 'story.mp4')
            if os.path.exists(video_path):
                self.presence('Story Mode', 'Playing local story preview')
                self.transition_to(self.video)
                from pathlib import Path
                self.video.play_item('STORY', Path(video_path))
            else:
                self.presence('Story Mode', 'Preview unavailable')
                self.transition_to(self.info)

    def dev_action(self, item):
        routes = {
            'build_information': self.info,
            'console': self.console,
            'build_pipeline': self.pipeline,
        }
        if item in routes:
            self.transition_to(routes[item])
        else:
            self.transition_to(self.info)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F11:
            self.showNormal() if self.isFullScreen() else self.showFullScreen()
            return
        if event.key() == Qt.Key.Key_Escape:
            if self.stack.currentWidget() not in (self.boot, self.loading, self.menu):
                self.show_menu()
                return
        super().keyPressEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    icon = os.path.join(get_asset_path(''), 'icon.ico')
    if os.path.exists(icon):
        app.setWindowIcon(QIcon(icon))
    window = MainApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
