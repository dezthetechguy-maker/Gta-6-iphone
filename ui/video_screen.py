from pathlib import Path
from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import QWidget, QVBoxLayout


class VideoScreen(QWidget):
    """Borderless, full-screen video playback screen."""

    finished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:#000;")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.player = QMediaPlayer(self)
        self.audio = QAudioOutput(self)
        self.player.setAudioOutput(self.audio)
        self.video = QVideoWidget(self)
        self.video.setStyleSheet("background:#000; border:0; margin:0; padding:0;")
        self.video.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
        self.player.setVideoOutput(self.video)

        # The video itself fills the entire window. No title, borders, BACK
        # button, status bar, or other overlays are shown while playing.
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.video, 1)

        self.player.mediaStatusChanged.connect(self._media_status)
        self.player.errorOccurred.connect(self._error)
        self.audio.setVolume(0.85)
        self.current_item = None
        self._last_error = ""

    def play_item(self, item: str, path: Path):
        self.current_item = item
        self._last_error = ""
        self.player.stop()
        self.player.setSource(QUrl.fromLocalFile(str(path)))
        self.show()
        self.setFocus(Qt.FocusReason.OtherFocusReason)
        self.player.play()

    def _media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.player.stop()
            self.finished.emit()

    def _error(self, _error, error_string):
        self._last_error = error_string or "VIDEO ERROR"

    def back(self):
        self.player.stop()
        self.finished.emit()

    def keyPressEvent(self, e: QKeyEvent):
        if e.key() == Qt.Key.Key_Escape:
            self.back()
        elif e.key() == Qt.Key.Key_Space:
            if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                self.player.pause()
            else:
                self.player.play()
        elif e.key() == Qt.Key.Key_F11:
            window = self.window()
            window.showNormal() if window.isFullScreen() else window.showFullScreen()
        else:
            super().keyPressEvent(e)
