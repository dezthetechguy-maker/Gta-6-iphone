from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel

class DevConsole(QWidget):
    def __init__(self, on_back):
        super().__init__()
        self.on_back = on_back
        self.setStyleSheet("background-color: rgba(0,0,0,0.9);")

        layout = QVBoxLayout()

        # Output
        self.output = QTextEdit()
        self.output.setStyleSheet("""
            QTextEdit {
                background: #0a0a0a;
                color: #33ff66;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                border: 1px solid #33ff66;
                padding: 10px;
            }
        """)
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        # Input
        input_layout = QHBoxLayout()
        self.prompt = QLabel("> ")
        self.prompt.setStyleSheet("color: #33ff66; font-size: 16px;")
        self.input = QLineEdit()
        self.input.setStyleSheet("""
            QLineEdit {
                background: #0a0a0a;
                color: #33ff66;
                font-family: 'Courier New', monospace;
                font-size: 16px;
                border: none;
                border-bottom: 1px solid #33ff66;
            }
        """)
        self.input.returnPressed.connect(self.execute_command)
        input_layout.addWidget(self.prompt)
        input_layout.addWidget(self.input)
        layout.addLayout(input_layout)

        # Commands
        self.commands = {
            "help": "Available commands: status, build, world, weather, fps, clear, exit",
            "status": "System: ONLINE\nFPS: 60\nEntities: 1427\nMemory: 7421 MB",
            "build": "Build ID: VC-ALPHA-4217\nStatus: SUCCESS",
            "world": "World: VICE_CITY\nStreaming: ACTIVE",
            "weather": "Current: SUNSET\nNext: NIGHT",
            "fps": "FPS: 119\nFrame: 8.4ms\nGPU: 64%\nCPU: 31%",
            "clear": "CLEAR",
            "exit": "EXIT"
        }

        # Back button
        back_btn = QPushButton("BACK")
        back_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #ffffff;
                border: 1px solid #ffffff;
                padding: 8px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.1);
            }
        """)
        back_btn.clicked.connect(self.on_back)
        layout.addWidget(back_btn, alignment=Qt.AlignRight)

        self.setLayout(layout)

        self.append_output("VICE CITY DEV CONSOLE v1.0")
        self.append_output("Type 'help' for commands.")

    def append_output(self, text):
        self.output.append(text)
        self.output.verticalScrollBar().setValue(self.output.verticalScrollBar().maximum())

    def execute_command(self):
        cmd = self.input.text().strip().lower()
        self.input.clear()
        if not cmd:
            return
        self.append_output(f"> {cmd}")
        if cmd in self.commands:
            resp = self.commands[cmd]
            if resp == "CLEAR":
                self.output.clear()
            elif resp == "EXIT":
                self.on_back()
            else:
                self.append_output(resp)
        else:
            self.append_output(f"Unknown command: '{cmd}'. Type 'help'.")
