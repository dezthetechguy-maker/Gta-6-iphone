from PySide6.QtMultimedia import QSoundEffect, QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl
from utils.paths import get_audio_path
import os

class AudioManager:
    def __init__(self):
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.sound_effects = {}
        self.music_loaded = False

    def load_sound(self, name, filename):
        """Load a sound effect (wav)"""
        path = get_audio_path(filename)
        if os.path.exists(path):
            effect = QSoundEffect()
            effect.setSource(QUrl.fromLocalFile(path))
            self.sound_effects[name] = effect
            return True
        return False

    def play_sound(self, name):
        if name in self.sound_effects:
            self.sound_effects[name].play()

    def load_music(self, filename):
        path = get_audio_path(filename)
        if os.path.exists(path):
            self.player.setSource(QUrl.fromLocalFile(path))
            self.music_loaded = True
            return True
        return False

    def play_music(self, loop=True):
        if self.music_loaded:
            self.player.play()
            if loop:
                self.player.mediaStatusChanged.connect(self._loop_music)

    def _loop_music(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.player.play()

    def stop_music(self):
        self.player.stop()

    def set_volume(self, volume):
        self.audio_output.setVolume(volume)
