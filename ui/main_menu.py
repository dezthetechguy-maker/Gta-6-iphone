from pathlib import Path

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPainter, QColor, QFont, QPixmap

from utils.assets import find_tab_preview
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame


class MenuTab(QFrame):
    clicked = Signal(str)

    def __init__(self, key, title, description, image=None, parent=None):
        super().__init__(parent)
        self.key = key
        self.image_path = image
        self.setObjectName('MenuTab')
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumSize(250, 185)
        self.setStyleSheet('''
            QFrame#MenuTab { background: rgba(8,10,15,205); border: 1px solid rgba(255,255,255,45); }
            QFrame#MenuTab:hover { background: rgba(25,18,28,225); border: 2px solid #ff4fb3; }
            QLabel { background: transparent; }
        ''')
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.image = QLabel()
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image.setMinimumHeight(105)
        self.image.setStyleSheet('background: rgba(0,0,0,80);')
        if image and image.exists():
            self._pixmap = QPixmap(str(image))
        else:
            self._pixmap = None
        lay.addWidget(self.image, 1)

        text = QWidget()
        text_lay = QVBoxLayout(text)
        text_lay.setContentsMargins(15, 9, 15, 10)
        text_lay.setSpacing(2)
        self.title = QLabel(title)
        self.title.setStyleSheet('color:white; font: 900 20px Arial; letter-spacing:1px;')
        self.desc = QLabel(description)
        self.desc.setStyleSheet('color:#b9c0ca; font: 11px Consolas;')
        self.desc.setWordWrap(True)
        text_lay.addWidget(self.title)
        text_lay.addWidget(self.desc)
        lay.addWidget(text)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._pixmap and not self._pixmap.isNull():
            self.image.setPixmap(self._pixmap.scaled(
                self.image.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.key)
        super().mousePressEvent(event)


class MainMenu(QWidget):
    '''Large, cinematic tab menu inspired by console game menus.'''
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        root = QVBoxLayout(self)
        root.setContentsMargins(55, 35, 55, 28)
        root.setSpacing(14)

        self.background = QPixmap()
        bg = Path(__file__).resolve().parents[1] / 'assets' / 'backgrounds' / 'menu.jpg'
        if bg.exists():
            self.background = QPixmap(str(bg))
        else:
            fallback = find_tab_preview('story')
            if fallback:
                self.background = QPixmap(str(fallback))

        head = QHBoxLayout()
        brand_box = QVBoxLayout()
        brand = QLabel('V I C E   C I T Y')
        brand.setStyleSheet('color:white; font: 900 48px Arial; letter-spacing:4px;')
        sub = QLabel('INTERNAL ALPHA ENVIRONMENT   //   BUILD 0.6.13   //   REVISION 4217')
        sub.setStyleSheet('color:#f1a4ca; font: 11px Consolas; letter-spacing:2px;')
        brand_box.addWidget(brand)
        brand_box.addWidget(sub)
        head.addLayout(brand_box)
        head.addStretch()
        status = QLabel('ONLINE\nDEV BUILD')
        status.setAlignment(Qt.AlignmentFlag.AlignRight)
        status.setStyleSheet('color:#8fe9ff; font: 700 11px Consolas;')
        head.addWidget(status)
        root.addLayout(head)

        root.addStretch(1)
        grid = QHBoxLayout()
        grid.setSpacing(12)
        tabs = [
            ('STORY', 'STORY MODE', 'PLAY THE CAMPAIGN / STORY VIDEO'),
            ('CHARACTERS', 'CHARACTERS', 'LUCIA / JASON CHARACTER TEST'),
            ('MAP', 'MAP', 'OPEN THE VICE CITY WORLD MAP'),
            ('OPTIONS', 'OPTIONS', 'DISPLAY / GRAPHICS / GAME SETTINGS'),
            ('DEVELOPER', 'DEVELOPER', 'DEV TOOLS / CONSOLE / BUILD PIPELINE'),
        ]
        for key, title, desc in tabs:
            image = find_tab_preview(key)
            if image is None:
                image = Path(__file__).resolve().parents[1] / 'assets' / 'backgrounds' / 'menu.jpg'
            tab = MenuTab(key, title, desc, image)
            tab.clicked.connect(self._clicked)
            grid.addWidget(tab, 1)
        root.addLayout(grid)
        root.addStretch(1)

        foot = QHBoxLayout()
        hint = QLabel('SELECT A TAB   •   ENTER / CLICK TO OPEN   •   ESC TO EXIT')
        hint.setStyleSheet('color:#d0d4da; font: 10px Consolas;')
        foot.addWidget(hint)
        foot.addStretch()
        exit_btn = QPushButton('EXIT')
        exit_btn.setFixedSize(95, 34)
        exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        exit_btn.setStyleSheet('''
            QPushButton { color:#fff; background:rgba(0,0,0,120); border:1px solid rgba(255,255,255,70); font:700 12px Arial; }
            QPushButton:hover { background:rgba(255,70,150,80); border:1px solid #ff4fb3; }
        ''')
        exit_btn.clicked.connect(lambda: self._clicked('EXIT'))
        foot.addWidget(exit_btn)
        root.addLayout(foot)

        self.tabs = tabs
        self.focus_index = 0

    def _clicked(self, key):
        # MainApp handles the actual screen transition.
        if hasattr(self, 'navigate'):
            self.navigate(key)

    def set_navigate_callback(self, callback):
        self.navigate = callback

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        if not self.background.isNull():
            scaled = self.background.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                            Qt.TransformationMode.SmoothTransformation)
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            p.drawPixmap(x, y, scaled)
        else:
            p.fillRect(self.rect(), QColor('#05060b'))
        p.fillRect(self.rect(), QColor(0, 0, 0, 105))
        super().paintEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self._clicked('EXIT')
        else:
            super().keyPressEvent(event)
