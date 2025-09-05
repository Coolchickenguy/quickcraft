import threading
from typing import Any
import requests
from urllib.parse import urljoin
import os
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QMessageBox,
    QSizePolicy,
    QDialog,
    QDialogButtonBox,
    QPushButton,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer
import sys
import subprocess
from assets_root import assets_root
from . import common, loaders, collapsibleSection
from .release_manifest import release_manifest
import shutil
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, utils


class confirmInvalidSignature(QDialog):
    def __init__(self, parent=None, fromUrl="unknown"):
        super().__init__(parent)
        self.setWindowTitle("Confirmation")
        self.setMinimumWidth(300)

        self.result = None

        # Layout
        layout = QVBoxLayout(self)

        # Main message
        label = QLabel(
            "Release is signed by a different author than this release. It is unsafe to continue, you may install unwanted software (Like a virus!). Vended by mirror "
            + fromUrl
        )
        layout.addWidget(label)

        # Discard update button
        discard_button = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        discard_button.accepted.connect(self.on_discard)
        layout.addWidget(discard_button)

        # Collapsible "Advanced" section
        advanced_section = collapsibleSection.CollapsibleSection("Advanced")
        advanced_layout = QVBoxLayout()
        continue_button = QPushButton("Continue anyway")
        continue_button.clicked.connect(self.on_continue)
        advanced_layout.addWidget(continue_button)
        advanced_section.setContentLayout(advanced_layout)

        layout.addWidget(advanced_section)

    def on_discard(self):
        self.result = "discard"
        self.accept()

    def on_continue(self):
        self.result = "continue"
        self.accept()

    def exec_dialog(self):
        self.exec()
        if self.result == "continue":
            return "continue"
        elif self.result == "discard":
            return "discard"
        return "cancel"


class Window(QWidget):
    statusLabel: common.ResizingTextLabel
    allowClose: bool = False
    rootUrl: str
    failed: bool = False
    def updater(
        self, latest_release: dict[str, Any], latest: str, rootUrl: str
    ) -> bool:
        self.failed = False
        if latest_release is None:
            raise Exception(
                "ERROR! ERROR! ERROR! Internal exception. Could not find refered version."
            )
        print(f"Latest release is NOT installed, latest is {latest}. Updating.")
        if release_manifest["platform"] == "win":
            dlPath = latest_release["win"]
            sigDlPath = latest_release["sig_win"]
        elif release_manifest["platform"] == "macos":
            dlPath = latest_release["macos"]
            sigDlPath = latest_release["sig_macos"]
        else:
            dlPath = latest_release["linux"]
            sigDlPath = latest_release["sig_linux"]
        print(f"Downloading new release {latest_release}")
        updateDlRequest = requests.request(method="get", url=urljoin(rootUrl, dlPath))
        publicKey = release_manifest["vendor"]["publicKey"]
        if publicKey != None:
            loadedPublicKey = serialization.load_pem_public_key(
                bytes(publicKey, "utf8")
            )
            sigDlRequest = requests.request(
                method="get", url=urljoin(rootUrl, sigDlPath)
            )
            hasher = hashes.Hash(hashes.SHA256())
            hasher.update(updateDlRequest.content)
            digest = hasher.finalize()
            try:
                loadedPublicKey.verify(
                    sigDlRequest.content,
                    digest,
                    padding.PKCS1v15(),
                    utils.Prehashed(hashes.SHA256()),
                )
                print("Signature is valid.")
            except Exception as e:
                print(f"Signature invalid: {e}")
                popup = confirmInvalidSignature(fromUrl=rootUrl)
                result = popup.exec_dialog()
                if result == "continue":
                    print("Continuing anyway (Not my fault if you get a virus)")
                else:
                    self.failed = True
                    return False
        print("Downloaded new release")
        tmpPath = os.path.join(assets_root, "update_temp")
        if release_manifest["platform"] == "win":
            import zipfile
            import io

            with zipfile.ZipFile(io.BytesIO(updateDlRequest.content)) as zip_ref:
                zip_ref.extractall(tmpPath)
        else:
            import tarfile
            import io

            with tarfile.open(
                fileobj=io.BytesIO(updateDlRequest.content), mode="r:gz"
            ) as tarObj:
                tarObj.extractall(path=tmpPath)
        print("Extraced update")
        p = subprocess.Popen(
            [
                sys.executable,
                os.path.join(tmpPath, "assets", "update_fromlast.py"),
                assets_root,
                release_manifest["version"],
                latest,
            ],
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        p.wait()
        while True:
            try:
                shutil.rmtree(tmpPath)
                break
            except Exception as e:
                print("Could not delete update temp. Retrying")
                print(e)
        print("Done update")
        self.safeClose()
        return True

    def safeClose(self):
        self.allowClose = True
        QTimer.singleShot(0, self.close)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.resize(600, 300)
        self.setWindowTitle("Quickcraft")
        self.setContentsMargins(20, 20, 20, 20)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        common.initBackround(self)
        common.initLogo(self, layout, stretch=3)
        self.statusLabel = common.ResizingTextLabel()
        self.statusLabel.label.setText("Checking for updates")
        self.statusLabel.label.setFont(QFont(common.families[0], 40))
        self.statusLabel.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self.statusLabel, stretch=1)
        loading = loaders.UnknownTimeProgressBar(fixed=False)
        loading.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(loading, stretch=2)

        # Layout finished
        def ensure_trailing_slash(url: str) -> str:
            return url if url.endswith("/") else url + "/"

        def findIndexJsons(rootUrls: list[str]) -> list[dict[str, Any]]:
            indexes: list[dict[str, Any]] = []
            for rootUrl in rootUrls:
                try:
                    dlRequest = requests.request(
                        method="get",
                        url=urljoin(
                            ensure_trailing_slash(rootUrl), "release_index.json"
                        ),
                    )
                    self.rootUrl = rootUrl
                    indexes.append({"url": rootUrl, "index": dlRequest.json()})
                except Exception as e:
                    import warnings

                    warnings.warn(
                        message=f"Mirror not avalible, request failed. error: {e}",
                        category=Warning,
                    )
            if len(indexes) == 0:
                warnings.warn(
                    message="Could not check for updates, all mirrors failed. Skipping.",
                    category=Warning,
                )
                self.safeClose()
            return indexes

        res = findIndexJsons(release_manifest["vendor"]["rootUrl"].split("|"))
        if len(res) == 0:
            return

        def compareVersions(versions: list[str]):
            split = list(
                map(
                    lambda version: list(map(lambda seg: int(seg), version.split("."))),
                    versions,
                )
            )
            leaders = [split]
            for i in range(0, 3):
                top = max(map(lambda a: a[i], leaders[0]))
                leaders[0] = list(filter(lambda a: a[i] == top, leaders[0]))
            return ".".join(list(map(lambda seg: str(seg), leaders[0][0])))

        latestList: list[dict[str, Any]] = []
        for index in res:
            latest = compareVersions(
                list(
                    map(
                        lambda x: x["version"],
                        list(
                            filter(
                                lambda x: x["channel"] == release_manifest["channel"],
                                index["index"]["releases"],
                            )
                        ),
                    )
                )
            )
            if latest == release_manifest["version"]:
                continue
            for release in index["index"]["releases"]:
                if release["version"] == latest:
                    latest_release = release
                    break
            latestList.append({"release": latest_release, "url": index["url"]})

        def next():
            latest = compareVersions(
                list(map(lambda latest: latest["release"]["version"], latestList))
            )
            for releaseIndex in range(len(latestList)):
                if latestList[releaseIndex]["release"]["version"] == latest:
                    latestIndex = releaseIndex
                    break

            reply = QMessageBox.question(
                self,
                "Update Confirmation",
                f"Do you want to update from {release_manifest['version']} to newer version {latest} from mirror {latestList[latestIndex]["url"]}",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
                | QMessageBox.StandardButton.NoAll,
                QMessageBox.StandardButton.Yes,
            )
            if reply == QMessageBox.StandardButton.NoAll:
                return
            elif reply == QMessageBox.StandardButton.No:
                latestList.pop(releaseIndex)
                if len(latestList) == 0:
                    return
                else:
                    next()
            else:
                self.statusLabel.label.setText(f"Updating from mirror {latestList[latestIndex]["url"]}")
                taskUuid = common.TaskManager.startTask(
                    threading.Thread(
                        target=self.updater,
                        args=[
                            latestList[latestIndex]["release"],
                            latest,
                            latestList[latestIndex]["url"],
                        ],
                    )
                )
                def wrap(uuid):
                    if not self.failed:
                        latestList.pop(releaseIndex)
                        if len(latestList) == 0:
                            pass
                        else:
                            next()

                common.TaskManager.onEnd(taskUuid, wrap)
        next()
        self.safeClose()

    def closeEvent(self, event):
        if self.allowClose:
            event.accept()
        else:
            event.ignore()


def startApp():
    window = Window()
    window.show()
    sys.exit(common.app.exec())


if __name__ == "__main__":
    startApp()
