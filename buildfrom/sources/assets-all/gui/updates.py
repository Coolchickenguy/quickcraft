import requests
from urllib.parse import urljoin
import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMessageBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer
import sys
import subprocess
from assets_root import assets_root
from . import common, loaders
from .release_manifest import release_manifest
import shutil
import threading

class Window(QWidget):
    statusLabel: QLabel
    allowClose: bool = False
    #bdcpmInstance:common.TaskManagerClass.bidirectionalCrossProcessControlManager

    def updater(self,latest_release,latest):
        if latest_release is None:
                raise Exception("ERROR! ERROR! ERROR! Internal exception. Could not find refered version.")
        print(f"Latest release is NOT installed, latest is {latest}. Updating.")
        if release_manifest["platform"] == "win":
            dlPath=latest_release["win"]
        elif release_manifest["platform"] == "macos":
            dlPath=latest_release["macos"]
        else:
            dlPath=latest_release["linux"]
        print(f"Downloading new release {latest_release}")
        updateDlRequest=requests.request(method="get",url=urljoin(release_manifest["vendor"]["rootUrl"],dlPath))
        print("Downloaded new release")
        tmpPath = os.path.join(assets_root,"update_temp")
        if release_manifest["platform"] == "win":
            import zipfile
            import io
            with zipfile.ZipFile(io.BytesIO(updateDlRequest.content)) as zip_ref:
                zip_ref.extractall(tmpPath)
        else:
            import tarfile
            import io
            with tarfile.open(fileobj=io.BytesIO(updateDlRequest.content),mode="r:gz") as tarObj:
                tarObj.extractall(path=tmpPath)
        print("Extraced update")
        p = subprocess.Popen([sys.executable,os.path.join(tmpPath,"assets","update_fromlast.py"),assets_root,release_manifest["version"],latest],stdout=sys.stdout,stderr=sys.stderr)
        p.wait()
        while True:
            try:
                shutil.rmtree(tmpPath)
                break
            except Exception as e:
                print("Could not delete update temp. Retrying")
                print(e)
        print("Done update")
        #self.bdcpmInstance.proxyOtherSideFunction("safeClose",False)()
        self.safeClose()

    def safeClose(self):
        self.allowClose = True
        QTimer.singleShot(0, self.close)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.resize(600, 300)
        self.setWindowTitle("Quickcraft")
        self.setContentsMargins(20, 20, 20, 20)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        common.initBackround(self)
        common.initLogo(self,layout)
        self.statusLabel = QLabel()
        self.statusLabel.setText("Checking for updates")
        self.statusLabel.setFont(QFont(common.families[0], 40))
        self.statusLabel.adjustSize()
        layout.addWidget(self.statusLabel,alignment=Qt.AlignmentFlag.AlignCenter)
        loading = loaders.UnknownTimeProgressBar()
        layout.addWidget(loading,alignment=Qt.AlignmentFlag.AlignCenter)
        # Layout finished

        try:
            dlRequest = requests.request(method="get",url=urljoin(release_manifest["vendor"]["rootUrl"],"release_index.json"))
            res=dlRequest.json() 
        except Exception as e:
            import warnings
            warnings.warn(message=f"Could not check for updates, request failed. error: {e.with_traceback()}",category=Warning)
            self.safeClose()
        def compareVersions(versions:list[str]):
            split = list(map(lambda version: list(map(lambda seg: int(seg),version.split("."))),versions))
            leaders=[split]
            for i in range(0,3):
                top=max(map(lambda a:a[i],leaders[0]))
                leaders[0] = list(filter(lambda a:a[i] == top,leaders[0]))
            return ".".join(list(map(lambda seg: str(seg),leaders[0][0])))
        latest=compareVersions(list(map(lambda x: x["version"],list(filter(lambda x: x["channel"] == release_manifest["channel"], res["releases"])))))
        if latest != release_manifest["version"]:
            reply = QMessageBox.question(
                self,
                "Update Confirmation",
                f"Do you want to update from {release_manifest['version']} to newer version {latest}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes,
            )
            if reply == QMessageBox.StandardButton.No:
                self.safeClose()
                return
            for release in res["releases"]:
                if release["version"] == latest:
                    latest_release = release
            #self.bdcpmInstance = common.TaskManager.bidirectionalCrossProcessControlManager()
            taskUuid = common.TaskManager.startTask(threading.Thread(target=self.updater,args=[latest_release,latest]))
            #self.bdcpmInstance.handleCalls(self)
        else:
            self.safeClose()



    def closeEvent(self, event):
        if self.allowClose:
            #if self.bdcpmInstance is not None:
            #    self.bdcpmInstance.stopped = True
            event.accept()
        else:
            event.ignore()

def startApp():
    window = Window()
    #window.setWindowIcon(QIcon('../logo.ico'))
    window.show()
    sys.exit(common.app.exec())
if __name__ == "__main__":
    startApp()