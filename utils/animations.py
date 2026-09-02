from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QPoint, QRectF
from PySide6.QtWidgets import QWidget

def fade_in(widget, duration=500):
    anim = QPropertyAnimation(widget, b"windowOpacity")
    anim.setDuration(duration)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
    anim.start()
    return anim

def fade_out(widget, duration=500, callback=None):
    anim = QPropertyAnimation(widget, b"windowOpacity")
    anim.setDuration(duration)
    anim.setStartValue(1.0)
    anim.setEndValue(0.0)
    anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
    if callback:
        anim.finished.connect(callback)
    anim.start()
    return anim

def slide_in(widget, start_pos, end_pos, duration=400):
    anim = QPropertyAnimation(widget, b"pos")
    anim.setDuration(duration)
    anim.setStartValue(start_pos)
    anim.setEndValue(end_pos)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    anim.start()
    return anim

def scale_anim(widget, start, end, duration=500):
    anim = QPropertyAnimation(widget, b"scale")
    anim.setDuration(duration)
    anim.setStartValue(start)
    anim.setEndValue(end)
    anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
    anim.start()
    return anim
