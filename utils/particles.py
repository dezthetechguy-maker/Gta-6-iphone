from PySide6.QtCore import QObject, QTimer, Qt
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QWidget
import random, math

class ParticleOverlay(QWidget):
    def __init__(self,parent=None, mode='ambient'):
        super().__init__(parent); self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents); self.p=[]; self.mode=mode
        self.t=QTimer(self); self.t.timeout.connect(self.tick); self.t.start(33)
    def tick(self):
        w=max(1,self.width()); h=max(1,self.height())
        if len(self.p)<70:
            self.p.append([random.random()*w, random.random()*h, random.uniform(.2,1.4), random.uniform(.4,1.8), random.random()*2*math.pi])
        for q in self.p:
            q[1]+=q[2]; q[0]+=math.sin(q[4]+q[1]*.005)*.25
            if q[1]>h+4: q[0]=random.random()*w; q[1]=-4
        self.update()
    def paintEvent(self,_):
        p=QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        for x,y,r,a,_ in self.p:
            c=QColor(255,180,220); c.setAlphaF(.10*a); p.setPen(Qt.PenStyle.NoPen); p.setBrush(c); p.drawEllipse(int(x),int(y),int(r),int(r))
