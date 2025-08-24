from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QMessageBox, QSizePolicy
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal
import sys
from .bindings import install, bindings
from . import loaders, common


class Window(QWidget):
    closed = pyqtSignal()
    max_progress = 0
    installer: install.install
    statusLabel: common.ResizingTextLabel

    def setStatus(self, status):
        self.statusLabel.label.setText(status)
        self.statusLabel.adjustSize()

    def setMax(self, max):
        self.max_progress = max

    def setProgress(self, progress):
        self.loading.progress = (progress / self.max_progress) * 100
        self.loading.update()

    def install(self, version):
        self.installer = install.install(version=version, gui=self)

    def __init__(self, version):
        super().__init__()
        self.resize(600, 300)
        self.setWindowTitle("Quickcraft")
        self.setContentsMargins(20, 20, 20, 20)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        common.initBackround(self)
        common.initLogo(self, layout, stretch=4)
        self.statusLabel = common.ResizingTextLabel()
        self.statusLabel.label.setText("Idle")
        self.statusLabel.label.setFont(QFont(common.families[0], 40))
        self.statusLabel.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self.statusLabel, stretch=2)
        loading = loaders.PercentProgressBar(fixed=False)
        loading.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(loading, stretch=3)
        self.loading = loading
        self.install(bindings.latest_ver())

    def closeEvent(self, event):
        super().closeEvent(event)
        if self.installer != None and self.installer.done:
            event.accept()
            self.closed.emit()
        else:
            reply = QMessageBox.question(
                self,
                "Corrupting Your Minecraft Instance Confirmation",
                "Are you sure you want to force kill minecraft installation (BREAKS THINGS)",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                if self.installer != None:
                    self.installer.kill()
                    event.accept()
                    self.closed.emit()
                print("Force killed install")
            else:
                event.ignore()


if __name__ == "__main__":
    window = Window("1.21.5")
    window.show()
    sys.exit(common.app.exec())
