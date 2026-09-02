import os
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout, QFrame
from PySide6.QtGui import QPixmap

from utils.assets import find_tab_background, find_tab_image

from utils.assets import load_image

class CharacterSelect(QWidget):
    def __init__(self, on_back):
        super().__init__()
        self.on_back = on_back
        self.setStyleSheet("background: transparent;")
        self._background = find_tab_background('characters')
        self._background_pix = QPixmap(str(self._background)) if self._background else QPixmap()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("CHARACTERS")
        title.setStyleSheet("color: #ffffff; font-size: 36px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Grid of characters
        grid = QGridLayout()
        grid.setSpacing(30)

        characters = [
            ("Lucia", "lucia.webp"),
            ("Jason", "jason.webp")
        ]

        self.char_buttons = []
        for i, (name, img_file) in enumerate(characters):
            frame = QFrame()
            frame.setFrameShape(QFrame.Box)
            frame.setStyleSheet("border: 2px solid #333; background: rgba(20,20,30,0.7);")
            vbox = QVBoxLayout(frame)
            # Image
            pix_path = find_tab_image("characters", Path(img_file).stem)
            pix = QPixmap(str(pix_path)) if pix_path else load_image(os.path.join("characters", img_file), fallback_color="#2a2a3a", fallback_text=name)
            if not pix.isNull():
                pix = pix.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            label = QLabel()
            label.setPixmap(pix)
            label.setAlignment(Qt.AlignCenter)
            vbox.addWidget(label)
            # Name
            name_label = QLabel(name)
            name_label.setStyleSheet("color: #ffffff; font-size: 18px;")
            name_label.setAlignment(Qt.AlignCenter)
            vbox.addWidget(name_label)
            # Info
            info_label = QLabel("STATUS: ACTIVE\nLOCATION: VICE CITY")
            info_label.setStyleSheet("color: #88aaff; font-size: 12px;")
            info_label.setAlignment(Qt.AlignCenter)
            vbox.addWidget(info_label)
            # Button
            btn = QPushButton("Select")
            btn.setStyleSheet("""
                QPushButton {
                    background: #48dbfb;
                    color: black;
                    border: none;
                    padding: 8px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background: #0abde3;
                }
            """)
            btn.clicked.connect(lambda checked, n=name: self.select_character(n))
            vbox.addWidget(btn)
            grid.addWidget(frame, i//2, i%2)

        layout.addLayout(grid)

        back_btn = QPushButton("BACK")
        back_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #ffffff;
                border: 1px solid #ffffff;
                padding: 10px 30px;
                margin: 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.1);
            }
        """)
        back_btn.clicked.connect(self.on_back)
        layout.addWidget(back_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self._background_pix.isNull():
            self._background_pix_scaled = self._background_pix.scaled(
                self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation)
        self.update()

    def paintEvent(self, event):
        from PySide6.QtGui import QPainter, QColor
        p = QPainter(self)
        if not self._background_pix.isNull():
            pm = getattr(self, '_background_pix_scaled', self._background_pix)
            x = (self.width() - pm.width()) // 2
            y = (self.height() - pm.height()) // 2
            p.drawPixmap(x, y, pm)
        p.fillRect(self.rect(), QColor(0, 0, 0, 145))
        p.end()

    def select_character(self, name):
        # Could show a popup or just return
        self.on_back()
