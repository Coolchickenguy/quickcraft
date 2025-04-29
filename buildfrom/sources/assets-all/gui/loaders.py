import sys
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QApplication, QWidget
import math
from . import common
def sinDeg(x):
    return math.sin(math.radians(x))

class UnknownTimeProgressBar(QWidget):
    closed = pyqtSignal()
    timer:QTimer

    def __del__(self):
        self.timer.stop()
    def __init__(self, parent=None, width=600, height=70, border_width=2, border_radius=15, sine_factor=8):
        super().__init__(parent)

        # Set the initial progress and size of the progress bar
        self.progress = 0
        self.setFixedSize(width, height)

        # Create a timer to update the progress
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(50)  # Update every 50ms

        # Set attributes
        self.border_width = border_width
        self.border_radius = border_radius
        self.sine_factor = sine_factor

    def update_progress(self):
        #int(math.degrees((math.sin(math.radians(abs(38-self.progress))))/360)*self.sine_factor)
        self.progress = (self.progress+1)+abs(int(sinDeg(abs(38-self.progress))*self.sine_factor))
        if self.progress > 100:
            self.progress = 0  # Reset progress after reaching 100%

        # Update the widget to reflect the progress change
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        # Enable antialiasing for smoother curves
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Set the border pen
        pen = painter.pen()

        pen.setWidth(self.border_width)
        pen.setColor(QColor(0, 0, 0))  # Black border
        painter.setPen(pen)

        # Set the background brush
        painter.setBrush(QColor(200, 200, 200))  # Light gray

        # The width-border
        realWidth = self.width()-(self.border_width)
        realHeight = self.height()-(self.border_width)

        # Draw rounded background with border
        painter.drawRoundedRect(1, 1, realWidth, realHeight, self.border_radius, self.border_radius)

        # Draw the progress bar
        progress_width = (self.progress / 100) * realWidth

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 255))  # Blue fill
        pw_int=int(progress_width)+self.border_width
        defaultWidth = int(realWidth * 0.25)
        borderedHeight=self.height()-(self.border_width*2)
        if pw_int+defaultWidth <= realWidth:
            painter.drawRoundedRect(pw_int, self.border_width, defaultWidth, borderedHeight,self.border_radius-self.border_width,self.border_radius-self.border_width)
        else:
            rectWidth = realWidth-pw_int
            painter.drawRoundedRect(pw_int, self.border_width, rectWidth, borderedHeight,self.border_radius-self.border_width,self.border_radius-self.border_width)
            painter.drawRoundedRect(0+self.border_width, self.border_width,defaultWidth-rectWidth,borderedHeight,self.border_radius-self.border_width,self.border_radius-self.border_width)

class PercentProgressBar(QWidget):
    closed = pyqtSignal()

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()

    def __init__(self, parent=None, width=600, height=70, border_width=2, border_radius=15):
        super().__init__(parent)

        # Set the initial progress and size of the progress bar
        self.progress = 0
        self.setFixedSize(width, height)

        # Set attributes
        self.border_width = border_width
        self.border_radius = border_radius

    def paintEvent(self, event):
        painter = QPainter(self)

        # Enable antialiasing for smoother curves
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Set the border pen
        pen = painter.pen()

        pen.setWidth(self.border_width)
        pen.setColor(QColor(0, 0, 0))  # Black border
        painter.setPen(pen)

        # Set the background brush
        painter.setBrush(QColor(200, 200, 200))  # Light gray

        # Draw rounded background with border
        painter.drawRoundedRect(1, 1, self.width()-self.border_width, self.height()-self.border_width, self.border_radius, self.border_radius)

        # Draw the progress bar
        progress_width = int((self.progress / 100) * (self.width()-(self.border_width*2)))

        # Optionally set a transparent pen (no border on the progress part)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 255))  # Blue fill
        borderedHeight=self.height()-(self.border_width*2)
        painter.drawRoundedRect(self.border_width, self.border_width, progress_width, borderedHeight,self.border_radius-self.border_width,self.border_radius-self.border_width)

if __name__ == "__main__":

    window = UnknownTimeProgressBar()
    window.show()

    window2 = PercentProgressBar()
    window2.show()
    window2.progress = 50
    window2.update()

    sys.exit(common.app.exec())
