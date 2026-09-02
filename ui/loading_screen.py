from pathlib import Path

from PySide6.QtCore import QTimer, Signal, Qt, QUrl
from PySide6.QtGui import QPainter, QLinearGradient, QColor, QFont
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

from utils.particles import ParticleOverlay
from config import BUILD, REVISION


class LoadingScreen(QWidget):
    finished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:#000; color:#fff;")
        self.assets = Path(__file__).resolve().parents[1] / "assets"
        self.video_path = self.assets / "videos" / "loading.mp4"
        self.fallback_timer = QTimer(self)
        self.fallback_timer.setSingleShot(True)
        self.fallback_timer.timeout.connect(self._finish)
        self._finished = False

        self.player = QMediaPlayer(self)
        self.audio = QAudioOutput(self)
        self.player.setAudioOutput(self.audio)
        self.audio.setVolume(0.9)
        self.video = QVideoWidget(self)
        self.player.setVideoOutput(self.video)

        self.hud = QLabel(
            f"PROJECT: VICE CITY    BRANCH: ALPHA_DEV    PLATFORM: PC    RENDER: DX12\n"
            f"BUILD {BUILD}    REVISION {REVISION}"
        )
        self.hud.setStyleSheet(
            "color:rgba(255,255,255,220); font:10px Consolas; "
            "background:rgba(0,0,0,90); padding:8px 10px;"
        )
        self.hud.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        self.particles = ParticleOverlay(self)
        self.particles.hide()

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self.video, 1)
        self.hud.setParent(self)
        self.hud.raise_()

        self.player.mediaStatusChanged.connect(self._media_status)
        self.player.errorOccurred.connect(self._media_error)

    def restart(self):
        self._finished = False
        self.fallback_timer.stop()
        self.video.show()
        self.video.setGeometry(self.rect())
        self.hud.setGeometry(18, 18, max(420, self.width() - 36), 55)
        self.hud.show()
        self.hud.raise_()
        self.particles.setGeometry(self.rect())
        self.particles.hide()
        self.player.stop()

        if self.video_path.exists():
            self.player.setSource(QUrl.fromLocalFile(str(self.video_path)))
            self.player.play()
        else:
            # Fallback so the build still starts if someone removes the video.
            self.video.hide()
            self.fallback_timer.start(5000)
            self.update()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.video.setGeometry(self.rect())
        self.hud.setGeometry(18, 18, max(420, self.width() - 36), 55)
        self.particles.setGeometry(self.rect())

    def showEvent(self, e):
        super().showEvent(e)
        self.video.setGeometry(self.rect())
        self.hud.setGeometry(18, 18, max(420, self.width() - 36), 55)

    def _media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self._finish()

    def _media_error(self, *_args):
        # Give the media backend a moment to fail before falling back.
        if not self._finished:
            self.video.hide()
            self.fallback_timer.start(2500)
            self.update()

    def _finish(self):
        if self._finished:
            return
        self._finished = True
        self.fallback_timer.stop()
        self.player.stop()
        self.finished.emit()

    def paintEvent(self, event):
        # Black fallback background beneath the video.
        p = QPainter(self)
        p.fillRect(self.rect(), Qt.GlobalColor.black)
        p.end()
