import os
from . import auth, start, install, common
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal
import sys
from .bindings import bindings, start as bindingsStart
from .release_manifest import release_manifest
from assets_root import assets_root

class Window(QWidget):
    startInst:bindingsStart.start
    isRunning:bool = False
    button:QPushButton

    closed = pyqtSignal()

    def on_start(self):
        if self.isRunning:
            return
        self.isRunning = True
        if self.button != None:
            self.button.setStyleSheet("background-color: gray;border-radius:15px;")
        def start_mc():
            window = start.Window()
            window.show()
            common.WinMan.add(window)
            def onMcClose():
                print("Minecraft closed")
                self.isRunning = False
                self.startInst = None
                self.button.setStyleSheet("background-color: green;border-radius:15px;")
            print("Bindings starting")
            self.startInst = bindingsStart.start(window,onMcClose)

        latest=bindings.latest_ver()
        if not bindings.installed(latest):
            installWindow = install.Window(latest)
            installWindow.show()
            
            common.WinMan.add(installWindow)
            common.WinMan.onClose(installWindow,start_mc)
        else:
            start_mc()

    def openAccountWindow(self):
        authWindow=auth.Window(auth.offical_mc_auth)
        authWindow.show()
        common.WinMan.add(authWindow)

    def __init__(self):
        super().__init__()

        self.resize(600, 300)
        version=release_manifest["version"]
        print("Starting quickcraft " + version)
        self.setWindowTitle("Quickcraft " + version)
        self.setContentsMargins(20, 20, 20, 20)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        common.initBackround(self)
        # Add acount icon
        buttonLabel = common.ResizableClickableLabel()
        pixmap = QPixmap(os.path.join(assets_root,"account.svg"))
        buttonLabel.setPixmap(pixmap)
        buttonLabel.clicked.connect(self.openAccountWindow)
        buttonLabel.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(buttonLabel, stretch=1)
        # Acount icon end
        common.initLogo(self,layout, stretch=4)
        button = common.ResizingButton("Start")
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        button.button.setFont(QFont(common.families[0], 12))
        button.button.setStyleSheet("background-color: green;border-radius:15px;")
        button.button.clicked.connect(self.on_start)
        layout.addWidget(button, stretch=3)
        self.button = button.button
    def closeEvent(self, event):
        if self.isRunning and self.startInst:
            self.startInst.close()
        self.closed.emit()
        event.accept()

def startApp():
    window = Window()
    #window.setWindowIcon(QIcon('../logo.ico'))
    window.show()
    sys.exit(common.app.exec())
if __name__ == "__main__":
    startApp()