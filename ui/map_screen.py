from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsEllipseItem
)
from PySide6.QtGui import QColor, QBrush, QPen, QPainter, QPixmap

from utils.assets import load_image, find_tab_background, find_tab_image


class MapView(QGraphicsView):
    """Map view with fit-to-window, smooth zoom, and robust slow panning."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._zoom = 1.0
        self._min_zoom = 1.0
        self._max_zoom = 4.0
        self._pan_speed = 0.16
        self._panning = False
        self._last_pos = None
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setMouseTracking(True)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Keep the whole map visible when the window changes size while at reset.
        if self._zoom <= self._min_zoom + 1e-6 and self.scene() is not None and not self._panning:
            self._fit_map()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if not delta:
            return

        factor = 1.10 if delta > 0 else 0.90
        target = self._zoom * factor
        if target < self._min_zoom:
            factor = self._min_zoom / self._zoom
            target = self._min_zoom
        elif target > self._max_zoom:
            factor = self._max_zoom / self._zoom
            target = self._max_zoom

        if abs(factor - 1.0) < 1e-6:
            event.accept()
            return

        self.scale(factor, factor)
        self._zoom = target
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._panning = True
            self._last_pos = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # If the left button was released outside the widget, Qt may not send
        # us a mouseReleaseEvent. Detect that here and immediately recover.
        if self._panning and not (QApplication.mouseButtons() & Qt.MouseButton.LeftButton):
            self._stop_pan()
            super().mouseMoveEvent(event)
            return

        if self._panning and self._last_pos is not None:
            now = event.position().toPoint()
            delta = now - self._last_pos
            self._last_pos = now

            # Slow, direct panning that remains usable at every zoom level.
            scale = max(self._zoom, 0.001)
            dx = -(delta.x() * self._pan_speed) / scale
            dy = -(delta.y() * self._pan_speed) / scale
            self.translate(dx, dy)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._stop_pan()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event):
        # leaveEvent receives a generic QEvent. Never call buttons() on it.
        # Keep the current drag alive only while the left mouse button is held;
        # mouseMoveEvent will clean up automatically after an outside release.
        if self._panning and not (QApplication.mouseButtons() & Qt.MouseButton.LeftButton):
            self._stop_pan()
        super().leaveEvent(event)

    def focusOutEvent(self, event):
        self._stop_pan()
        super().focusOutEvent(event)

    def _stop_pan(self):
        self._panning = False
        self._last_pos = None
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def _fit_map(self):
        if self.scene() is None or self.scene().sceneRect().isNull():
            return
        self._stop_pan()
        self.resetTransform()
        self.fitInView(self.scene().sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self._zoom = self._min_zoom

    def reset_zoom(self):
        self._fit_map()

    def zoom_step(self, factor):
        target = self._zoom * factor
        if target < self._min_zoom:
            factor = self._min_zoom / self._zoom
            target = self._min_zoom
        elif target > self._max_zoom:
            factor = self._max_zoom / self._zoom
            target = self._max_zoom
        if abs(factor - 1.0) < 1e-6:
            return
        self.scale(factor, factor)
        self._zoom = target


class MapScreen(QWidget):
    def __init__(self, on_back):
        super().__init__()
        self.on_back = on_back
        self.setStyleSheet("background: transparent;")
        self._background = find_tab_background("map")
        self._background_pix = QPixmap(str(self._background)) if self._background else QPixmap()

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("VICE CITY MAP")
        title.setStyleSheet("color: #ffffff; font-size: 32px; font-weight: 900; letter-spacing: 4px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.view = MapView()
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
        self.view.setStyleSheet("border: 2px solid #444; background-color: #000;")
        self.view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.view)

        map_path = find_tab_image("map", "map")
        map_pix = QPixmap(str(map_path)) if map_path else load_image("ui/map.webp", fallback_color="#1a2a3a", fallback_text="MAP NOT FOUND")
        if not map_pix.isNull():
            self.map_item = QGraphicsPixmapItem(map_pix)
            self.scene.addItem(self.map_item)

            markers = [
                ("SAFEHOUSE", 0.2, 0.3), ("GARAGE", 0.5, 0.2),
                ("MISSION", 0.7, 0.5), ("SHOP", 0.3, 0.7),
                ("BEACH", 0.8, 0.8), ("AIRPORT", 0.1, 0.8),
                ("DOWNTOWN", 0.5, 0.6)
            ]
            for name, x, y in markers:
                item = QGraphicsEllipseItem(
                    x * map_pix.width() - 10,
                    y * map_pix.height() - 10,
                    20,
                    20,
                )
                item.setBrush(QBrush(QColor(255, 100, 100)))
                item.setPen(QPen(Qt.GlobalColor.white, 2))
                item.setToolTip(name)
                self.scene.addItem(item)

            # Scene rect is exactly the map image, so fitInView can show every edge.
            self.scene.setSceneRect(self.map_item.boundingRect())
            self.view.reset_zoom()

        controls = QHBoxLayout()
        zoom_out = QPushButton("−")
        zoom_in = QPushButton("+")
        reset = QPushButton("FIT MAP")
        back_btn = QPushButton("BACK TO MENU")
        for btn in (zoom_out, zoom_in, reset):
            btn.setFixedSize(58 if btn is not reset else 140, 42)
        back_btn.setFixedSize(200, 42)

        for btn in (zoom_out, zoom_in, reset, back_btn):
            btn.setStyleSheet("""
                QPushButton {
                    background: #222;
                    color: #ffffff;
                    border: 1px solid #ffffff;
                    padding: 8px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #444;
                    border-color: #ff00ff;
                }
            """)

        zoom_out.clicked.connect(lambda: self.view.zoom_step(0.90))
        zoom_in.clicked.connect(lambda: self.view.zoom_step(1.10))
        reset.clicked.connect(self.view.reset_zoom)
        back_btn.clicked.connect(self.on_back)

        controls.addWidget(zoom_out)
        controls.addWidget(zoom_in)
        controls.addWidget(reset)
        controls.addStretch()
        hint = QLabel("WHEEL: ZOOM  •  DRAG: SLOW PAN  •  FIT MAP: SHOW FULL MAP")
        hint.setStyleSheet("color: #ffffff; font-size: 14px;")
        controls.addWidget(hint)
        controls.addStretch()
        controls.addWidget(back_btn)
        layout.addLayout(controls)
        self.setLayout(layout)

    def paintEvent(self, event):
        p = QPainter(self)
        if not self._background_pix.isNull():
            pm = self._background_pix.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            p.drawPixmap((self.width() - pm.width()) // 2, (self.height() - pm.height()) // 2, pm)
        p.fillRect(self.rect(), QColor(0, 0, 0, 160))
        p.end()
