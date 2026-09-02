import random
import time
from PySide6.QtCore import QTimer, Qt, QRect, QPoint
from PySide6.QtGui import QFont, QFontDatabase, QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel, QFrame

from config import TERMINAL_DURATION, TERMINAL_LINES_MIN, TERMINAL_LINES_MAX
from utils.assets import load_image

# Large pool of fictional filenames
FILENAMES = [
    "world_streaming.cpp", "world_partition.cpp", "world_loader.cpp",
    "city_runtime.cpp", "city_entities.bin", "vice_city_world.dat",
    "vice_city_world.rpf", "map_data.bin", "map_streaming.dat",
    "terrain_data.bin", "road_network.dat", "traffic_manager.cpp",
    "traffic_nodes.bin", "vehicle_manager.cpp", "vehicle_data.bin",
    "vehicle_physics.dat", "vehicle_streaming.cpp", "vehicle_audio.dat",
    "character_system.cpp", "character_loader.cpp", "character_data.bin",
    "character_streaming.dat", "npc_manager.cpp", "npc_data.bin",
    "crowd_system.cpp", "crowd_data.bin", "animation_system.cpp",
    "animation_database.dat", "facial_animation.bin", "animation_cache.bin",
    "weather_system.cpp", "weather_presets.dat", "rain_particles.bin",
    "cloud_system.cpp", "lighting_system.cpp", "lighting_data.bin",
    "sun_position.dat", "reflection_data.bin", "water_system.cpp",
    "ocean_data.dat", "beach_environment.bin", "audio_engine.cpp",
    "audio_banks.dat", "music_streaming.dat", "ambient_audio.bin",
    "ui_system.cpp", "menu_layout.dat", "menu_assets.bin",
    "camera_system.cpp", "camera_presets.dat", "cinematic_data.bin",
    "render_pipeline.cpp", "shader_cache.bin", "texture_streaming.dat",
    "texture_database.bin", "material_data.dat", "particle_system.cpp",
    "particle_presets.dat", "physics_engine.cpp", "physics_data.bin",
    "collision_data.dat"
]

STATUS_TYPES = ["[BUILD]", "[LOAD ]", "[INIT ]", "[LINK ]", "[PACK ]", "[CACHE]", "[SCAN ]", "[OK   ]"]
FILE_TYPES = ["SOURCE", "WORLD", "SYSTEM", "MODULE", "ASSET", "DATA", "STREAM", "CACHE", "CONFIG"]

class BootSequence(QWidget):
    def __init__(self, on_finished):
        super().__init__()
        self.on_finished = on_finished
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #0a0a0a;")
        self.setFixedSize(1920, 1080)  # Will be resized later

        # Terminal text widget
        self.terminal = QTextEdit(self)
        self.terminal.setGeometry(50, 50, self.width()-100, self.height()-100)
        self.terminal.setStyleSheet("""
            QTextEdit {
                background-color: rgba(10,10,10,0.9);
                color: #33ff66;
                border: 1px solid #33ff66;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                padding: 20px;
            }
        """)
        self.terminal.setReadOnly(True)
        self.terminal.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.terminal.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Header
        self.header = QLabel("VICE CITY DEVELOPMENT ENVIRONMENT", self)
        self.header.setStyleSheet("color: #33ff66; font-size: 16px; font-weight: bold; background: transparent;")
        self.header.move(50, 10)

        # Footer (fan-made mockup)
        self.footer = QLabel("FAN-MADE MOCKUP", self)
        self.footer.setStyleSheet("color: #888888; font-size: 10px; background: transparent;")
        self.footer.move(self.width()-200, self.height()-30)

        # Blinking cursor
        self.cursor_pos = QPoint(50, 100)  # will be updated

        self.lines = []
        self.line_index = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.add_line)
        self.start_time = time.time()

        # Generate all lines beforehand
        self.generate_lines()

        # Start sequence
        self.timer.start(5)  # extremely fast initial

        # We'll manage speed changes via elapsed time
        self.last_elapsed = 0

    def generate_lines(self):
        total = random.randint(TERMINAL_LINES_MIN, TERMINAL_LINES_MAX)
        self.lines = []
        # First few lines are fixed
        self.lines.append("[BOOT] VICE CITY DEVELOPMENT ENVIRONMENT")
        self.lines.append("[BOOT] Initializing build pipeline...")
        self.lines.append("[BOOT] Starting asset registry...")
        # Generate random lines
        for _ in range(total - 10):  # leave room for final lines
            status = random.choice(STATUS_TYPES)
            filename = random.choice(FILENAMES)
            ftype = random.choice(FILE_TYPES)
            self.lines.append(f"{status} file: {filename} | type: {ftype} | {random.choice(['loading','initialized','linked','packed','scanning','ready','built'])}")
        # Add progress lines interspersed
        for i in range(3):
            idx = random.randint(10, len(self.lines)-10)
            self.lines.insert(idx, f"[BUILD] modules: {random.randint(100,500)}/{random.randint(500,1000)}")
        # Final lines
        self.lines.append("[OK   ] build pipeline complete")
        self.lines.append("[OK   ] world assets loaded")
        self.lines.append("[OK   ] renderer initialized")
        self.lines.append("[OK   ] interface initialized")
        self.lines.append("[OK   ] development environment ready")
        self.lines.append("------------------------------------------")
        self.lines.append("VICE CITY DEVELOPMENT BUILD")
        self.lines.append("BUILD: ALPHA")
        self.lines.append(f"REVISION: {random.randint(4000, 4500)}")
        self.lines.append("------------------------------------------")
        self.lines.append("[ OK ]")

    def add_line(self):
        if self.line_index >= len(self.lines):
            self.timer.stop()
            # Wait a bit then fade out
            QTimer.singleShot(300, self.finish)
            return

        # Control speed based on elapsed time to target ~3 seconds
        elapsed = time.time() - self.start_time
        if elapsed < 0.5:
            # Initial start: steady
            count = random.randint(1, 2)
        elif elapsed < 1.5:
            # Mid-section: speed up
            count = random.randint(3, 7)
        elif elapsed < 2.5:
            # Late-section: slow down slightly
            count = random.randint(1, 3)
        else:
            # Final stretch: very slow and deliberate
            count = 1

        # Avoid going beyond limit
        for _ in range(count):
            if self.line_index < len(self.lines):
                line = self.lines[self.line_index]
                self.terminal.append(line)
                self.line_index += 1
            else:
                break

        # Scroll to bottom
        self.terminal.verticalScrollBar().setValue(self.terminal.verticalScrollBar().maximum())

        # If we are in the final phase, slow down the timer interval
        if elapsed > 2.5:
            self.timer.setInterval(50)  # slower

    def finish(self):
        # Fade out
        self.fade_out()

    def fade_out(self):
        self.hide()
        if self.on_finished:
            self.on_finished()

    def resizeEvent(self, event):
        # Adjust geometries
        self.terminal.setGeometry(50, 50, self.width()-100, self.height()-100)
        self.header.move(50, 10)
        self.footer.move(self.width()-200, self.height()-30)
