from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QCheckBox, QPushButton, QGroupBox
from PySide6.QtGui import QPixmap, QPainter, QColor

from utils.assets import find_tab_background

class SettingsScreen(QWidget):
    def __init__(self, on_back):
        super().__init__()
        self.on_back = on_back
        self.setStyleSheet("background: transparent;")
        self._background = find_tab_background("options")
        self._background_pix = QPixmap(str(self._background)) if self._background else QPixmap()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("OPTIONS")
        title.setStyleSheet("color: #ffffff; font-size: 32px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Display
        display_group = QGroupBox("Display")
        display_group.setStyleSheet("color: #ffffff; font-size: 16px; border: 1px solid #333;")
        disp_layout = QVBoxLayout()

        res_layout = QHBoxLayout()
        res_layout.addWidget(QLabel("Resolution:"))
        self.res_combo = QComboBox()
        self.res_combo.addItems(["1920x1080", "2560x1440", "3840x2160"])
        res_layout.addWidget(self.res_combo)
        disp_layout.addLayout(res_layout)

        self.fullscreen_check = QCheckBox("Fullscreen")
        self.fullscreen_check.setChecked(True)
        disp_layout.addWidget(self.fullscreen_check)

        self.vsync_check = QCheckBox("VSync")
        self.vsync_check.setChecked(True)
        disp_layout.addWidget(self.vsync_check)

        display_group.setLayout(disp_layout)
        layout.addWidget(display_group)

        # Graphics
        graphics_group = QGroupBox("Graphics")
        graphics_group.setStyleSheet("color: #ffffff; font-size: 16px; border: 1px solid #333;")
        graph_layout = QVBoxLayout()
        self.motion_blur = QCheckBox("Motion Blur")
        self.motion_blur.setChecked(True)
        graph_layout.addWidget(self.motion_blur)
        self.film_grain = QCheckBox("Film Grain")
        self.film_grain.setChecked(True)
        graph_layout.addWidget(self.film_grain)
        graphics_group.setLayout(graph_layout)
        layout.addWidget(graphics_group)

        # Audio
        audio_group = QGroupBox("Audio")
        audio_group.setStyleSheet("color: #ffffff; font-size: 16px; border: 1px solid #333;")
        audio_layout = QVBoxLayout()
        # Volume slider could be added
        audio_layout.addWidget(QLabel("Volume: (placeholder)"))
        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)

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
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        if not self._background_pix.isNull():
            pm = self._background_pix.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            p.drawPixmap((self.width() - pm.width()) // 2, (self.height() - pm.height()) // 2, pm)
        p.fillRect(self.rect(), QColor(0, 0, 0, 175))
        p.end()
