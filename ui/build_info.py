from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

class BuildInfo(QWidget):
    def __init__(self, on_back):
        super().__init__()
        self.on_back = on_back
        self.setStyleSheet("background-color: rgba(0,0,0,0.85);")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("BUILD INFORMATION")
        title.setStyleSheet("color: #00ff88; font-size: 28px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        info = QLabel("""
            PROJECT: VICE CITY
            BRANCH: ALPHA_DEV
            BUILD: 0.6.13
            REVISION: 4217
            PLATFORM: PS5
            RENDER: DX12
            STATUS: DEVELOPMENT
            DATE: 2026-08-31
            DISCORD APP ID: 1234567890
        """)
        info.setStyleSheet("color: #88aaff; font-size: 18px; font-family: 'Courier New';")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)

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
