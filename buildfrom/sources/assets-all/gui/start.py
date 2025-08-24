from PyQt6.QtWidgets import QWidget, QVBoxLayout, QMessageBox, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
import sys
from . import loaders, loaders, common
from .bindings import start


class Window(QWidget):

    closed = pyqtSignal()
    minecraftOpened: bool = False
    timer: QTimer
    startInst: start.start
    loader: loaders.UnknownTimeProgressBar

    def __init__(self):
        super().__init__()
        self.resize(600, 300)
        self.setWindowTitle("Quickcraft")
        self.setContentsMargins(20, 20, 20, 20)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        common.initBackround(self)
        common.initLogo(self, layout, stretch=2)
        loading = loaders.UnknownTimeProgressBar(fixed=False)
        loading.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(loading, stretch=1)

        # This is 100% required to prevent a hang of qt's event loop, calling directly from bidirectionalCrossProcessControlManager does not work
        def checkMinecraftOpened():
            if self.minecraftOpened:
                print("Minecraft opened")
                timer.stop()
                self.close()

        timer = QTimer()
        timer.timeout.connect(checkMinecraftOpened)
        timer.start(75)
        self.timer = timer

    def closeEvent(self, event):
        if self.minecraftOpened:
            self.timer.stop()
            event.accept()
            self.closed.emit()
        else:
            reply = QMessageBox.question(
                self,
                "Close Confirmation",
                "Are you sure you want to force kill minecraft? THIS MAY CORRUPT YOUR INSTANCE",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.timer.stop()
                event.accept()
                self.closed.emit()
                if self.startInst != None:
                    self.startInst.close()
            else:
                event.ignore()


if __name__ == "__main__":
    window = Window()
    window.show()
    sys.exit(common.app.exec())
