from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, QFrame

class BuildPipeline(QWidget):
    def __init__(self, on_back):
        super().__init__()
        self.on_back = on_back
        self.setStyleSheet("background-color: rgba(0,0,0,0.9);")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("BUILD PIPELINE")
        title.setStyleSheet("color: #00ff88; font-size: 32px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #00ff88;
                border-radius: 5px;
                text-align: center;
                color: white;
                background: #0a0a0a;
                height: 30px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #48dbfb, stop:1 #00ff88);
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.progress)

        self.status_label = QLabel("Initializing...")
        self.status_label.setStyleSheet("color: #88aaff; font-size: 18px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # File list
        self.files_label = QLabel("")
        self.files_label.setStyleSheet("color: #cccccc; font-size: 14px; font-family: 'Courier New';")
        self.files_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.files_label)

        # Simulate build
        self.step = 0
        self.files = [
            "world_streaming", "character_system", "vehicle_system",
            "lighting", "audio", "ui", "physics", "network", "renderer"
        ]
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_build)
        self.timer.start(300)

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

        self.total_steps = 100

    def update_build(self):
        if self.step >= self.total_steps:
            self.timer.stop()
            self.status_label.setText("BUILD COMPLETE\nBUILD ID: VC-ALPHA-4217\nTIME: 00:02:41\nSTATUS: SUCCESS")
            self.files_label.setText("")
            return

        self.step += 1
        self.progress.setValue(self.step)
        # Show current file
        idx = min(self.step // 10, len(self.files)-1)
        file = self.files[idx] if idx < len(self.files) else "finalizing"
        self.files_label.setText(f"COMPILING:\n{file}")
        if self.step < 50:
            self.status_label.setText(f"Compiling... {self.step}%")
        elif self.step < 80:
            self.status_label.setText(f"Linking... {self.step}%")
        else:
            self.status_label.setText(f"Packaging... {self.step}%")
