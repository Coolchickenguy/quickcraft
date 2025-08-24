# Adapted from a stackoverflow answer, counld not remember the url
# Good luck maintaining
# Does not handle changing state while animation is still running well with the color transition
from PyQt6.QtCore import QObject, QSize, QPointF, QPropertyAnimation, QEasingCurve, pyqtProperty, pyqtSlot, Qt
from PyQt6.QtGui import  QPainter, QLinearGradient, QGradient, QColor
from PyQt6.QtWidgets import QAbstractButton, QApplication

palettes=[{"shadow":QColor("#363636"),"light":QColor("#4c4c4c"),"button":QColor("#3d3d3d")},{"shadow":QColor("#70c8f0"),"light":QColor("#7fd7ff"),"button":QColor("#00b0ff")}]

class SwitchPrivate(QObject):
    colors=[[palettes[0],palettes[0],palettes[0]],[palettes[1],palettes[1],palettes[1]]]
    mPointer:'Switch'
    def __init__(self, q, parent=None):
        QObject.__init__(self, parent=parent)
        self.mPointer = q
        self.mPosition = 0.0
        self.mGradient = QLinearGradient()
        self.mGradient.setSpread(QGradient.Spread.PadSpread)

        self.animation = QPropertyAnimation(self)
        self.animation.setTargetObject(self)
        self.animation.setPropertyName(b'position')
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setDuration(500)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutExpo)

        for index in range(len(self.colors[0])):
            for key in self.colors[0][index].keys():
                attr=f"color-{str(index)}-{key}"
                self.setProperty(attr,self.colors[0][index][key])
                bgAnimation = QPropertyAnimation(self,bytes(attr,"utf8"))
                bgAnimation.setDuration(500)
                bgAnimation.setEasingCurve(QEasingCurve.Type.InOutCubic)
                bgAnimation.state = False
                def onFinish():
                    bgAnimation.isFinished = True
                bgAnimation.finished.connect(onFinish)
                animationAttr=f"animation-{str(index)}-{key}"
                setattr(self,animationAttr,bgAnimation)
        self.animation.finished.connect(self.mPointer.update)

    @pyqtProperty(float)
    def position(self):
        return self.mPosition

    @position.setter
    def position(self, value):
        self.mPosition = value
        self.mPointer.update()

    def draw(self, painter:QPainter):
        for index in range(len(self.colors[0])):
            for key in self.colors[0][index].keys():
                animationAttr=f"animation-{str(index)}-{key}"
                animation=getattr(self,animationAttr)
                if self.mPointer.isChecked():
                    animation.setStartValue(self.colors[0][index][key])
                    animation.setEndValue(self.colors[1][index][key])
                else:
                    animation.setStartValue(self.colors[1][index][key])
                    animation.setEndValue(self.colors[0][index][key])
                if self.mPointer.isChecked() != animation.state:
                    animation.start()
                    animation.state = self.mPointer.isChecked()

        # Main code
        r = self.mPointer.rect()
        margin = int(r.height()/10)
        painter.setPen(Qt.PenStyle.NoPen)
        # Border
        """self.mGradient.setColorAt(0, self.property("color-0-shadow").darker(130))
        self.mGradient.setColorAt(1, self.property("color-0-light").darker(130))
        self.mGradient.setStart(0, r.height())
        self.mGradient.setFinalStop(0, 0)
        painter.setBrush(self.mGradient)
        painter.drawRoundedRect(r, r.height()/2, r.height()/2)"""
        # Backround
        self.mGradient.setColorAt(0, self.property("color-1-shadow").darker(140))
        self.mGradient.setColorAt(1, self.property("color-1-light").darker(160))
        self.mGradient.setStart(0, 0)
        self.mGradient.setFinalStop(0, r.height())
        painter.setBrush(self.mGradient)
        painter.drawRoundedRect(r.adjusted(margin, margin, -margin, -margin), r.height()/2, r.height()/2)

        # Round slider
        self.mGradient.setColorAt(0, self.property("color-2-button").darker(130))
        self.mGradient.setColorAt(1, self.property("color-2-button"))

        painter.setBrush(self.mGradient)

        x = r.height()/2.0 + self.mPosition*(r.width()-r.height())
        painter.drawEllipse(QPointF(x, r.height()/2), r.height()/2-margin, r.height()/2-margin)

    @pyqtSlot(bool, name='animate')
    def animate(self, checked):
        self.animation.setDirection(QPropertyAnimation.Direction.Forward if checked else QPropertyAnimation.Direction.Backward)
        self.animation.start()
        


class Switch(QAbstractButton):
    def __init__(self, parent=None, initial=False):
        QAbstractButton.__init__(self, parent=parent)
        self.dPtr = SwitchPrivate(self)
        self.setCheckable(True)
        self.clicked.connect(self.dPtr.animate)
        if initial:
            self.click()

    def sizeHint(self):
        return QSize(84, 42)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.dPtr.draw(painter)

    def resizeEvent(self, event):
        self.update()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = Switch()
    w.show()
    sys.exit(app.exec())