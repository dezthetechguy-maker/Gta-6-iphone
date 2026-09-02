from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtGui import QPixmap, QPainter, QColor

from utils.assets import find_tab_background

class DeveloperMenu(QWidget):
    def __init__(self, on_option, on_back):
        super().__init__()
        self.on_option = on_option
        self.on_back = on_back
        self.setStyleSheet("background: transparent;")
        self._background = find_tab_background("developer")
        self._background_pix = QPixmap(str(self._background)) if self._background else QPixmap()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("DEVELOPER MENU")
        title.setStyleSheet("color: #00ff88; font-size: 32px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        options = [
            "BUILD INFORMATION", "ASSET TEST", "WORLD TEST",
            "LIGHTING TEST", "WEATHER", "CAMERA", "FPS OVERLAY",
            "CONSOLE", "BUILD PIPELINE"
        ]

        for opt in options:
            btn = QPushButton(opt)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #cccccc;
                    font-size: 18px;
                    border: none;
                    padding: 8px 20px;
                    margin: 3px;
                }
                QPushButton:hover {
                    color: #00ff88;
                    background: rgba(0,255,136,0.1);
                }
            """)
            btn.clicked.connect(lambda checked, o=opt.lower().replace(" ", "_"): self.on_option(o))
            layout.addWidget(btn, alignment=Qt.AlignCenter)

        # Discord App ID footer
        discord_label = QLabel("1543708194147410151")
        discord_label.setStyleSheet("color: #555; font-size: 12px; font-family: 'Courier New';")
        discord_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(discord_label)

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

    def paintEvent(self, event):
        p = QPainter(self)
        if not self._background_pix.isNull():
            pm = self._background_pix.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            p.drawPixmap((self.width() - pm.width()) // 2, (self.height() - pm.height()) // 2, pm)
        p.fillRect(self.rect(), QColor(0, 0, 0, 190))
        p.end()
