import time
import urllib.parse
import urllib
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
from . import common, sliders, skinPreview
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QMessageBox,
    QMenu,
    QInputDialog,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal, QUrl, QTimer, QPoint
from PyQt6.QtGui import QFont
import minecraft_launcher_lib
import json
from .bindings.auth import *


class loginWindow(QWidget):
    closed = pyqtSignal()
    browser: QWebEngineView

    def __init__(self):
        super().__init__()
        self.resize(600, 300)
        self.setWindowTitle("Quickcraft")
        self.setContentsMargins(20, 20, 20, 20)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        common.initBackround(self)
        # common.initLogo(self, layout)
        self.browser = QWebEngineView()
        layout.addWidget(self.browser)

    def closeEvent(self, event):
        super().closeEvent(event)
        event.accept()
        self.closed.emit()


class Window(QWidget):
    closed = pyqtSignal()
    skinprev: skinPreview = None

    def mkPreview(self, info: CompleteLoginResponse, index: int):
        try:
            if self.skinprev is not None:
                self.layout().removeWidget(self.skinprev)
                self.skinprev.deleteLater()
            skin = list(filter(lambda x: x["state"] == "ACTIVE", info["skins"]))[0]
            # I know the .upper() is not nessesary, but just in CASE (pun intended)
            self.skinprev = skinPreview.MinecraftViewer(
                skin_url=skin["url"], slim=(skin["variant"].upper() == "SLIM")
            )
            self.skinprev.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )
            self.layout().insertWidget(index, self.skinprev, 4)
        except Exception as e:
            print(e)

    def login(self):
        encoded = f"https://login.live.com/oauth20_authorize.srf?client_id={self.auth['clientId']}&response_type=code&scope=XboxLive.signin%20offline_access&redirect_uri={urllib.parse.quote(self.auth['redirectUrl'])}"
        browserWindow = loginWindow()

        common.WinMan.add(browserWindow)
        browser = browserWindow.browser
        browser.setUrl(QUrl(encoded))

        def handleChange(qurl: QUrl):
            url = qurl.toString()
            if minecraft_launcher_lib.microsoft_account.url_contains_auth_code(url):
                code = minecraft_launcher_lib.microsoft_account.get_auth_code_from_url(
                    url
                )
                browserWindow.close()
                try:
                    authRes = complete_login(
                        client_id=self.auth["clientId"],
                        client_secret=None,
                        redirect_uri=self.auth["redirectUrl"],
                        auth_code=code,
                    )
                except Exception as e:
                    print(e)
                    return

                common.settings.beginGroup("account")
                common.settings.setValue("authRes", json.dumps(authRes))
                common.settings.setValue("authObtainedAt", time.time())
                common.settings.setValue("loggedIn", True)
                common.settings.endGroup()
                QTimer.singleShot(0, browserWindow.close)

                self.mkPreview(authRes, self.layout().indexOf(self.loginButton))

        browser.urlChanged.connect(handleChange)
        browserWindow.show()

        def closeAuth():
            browser.urlChanged.disconnect(handleChange)
            # Get the default profile
            profile = QWebEngineProfile.defaultProfile()

            # Clear HTTP cache
            profile.clearHttpCache()

            # Clear all persistent storage (cookies, localStorage, etc.)
            profile.clearAllVisitedLinks()
            profile.cookieStore().deleteAllCookies()

        common.WinMan.onClose(browserWindow, closeAuth)

    def infoDialog(self, title, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

        result = msg_box.exec()

    def advanced(self):
        menu = QMenu(self)

        exportRefreshToken = menu.addAction("Export refresh token")
        importRefreshToken = menu.addAction("Import refresh token")

        def exportrt():
            if isNotLoggedIn():
                self.infoDialog("Not logged in", "You are not logged in")
            else:
                common.settings.beginGroup("account")
                info = json.loads(common.settings.value("authRes"))
                self.infoDialog("Refresh token", info["refresh_token"])
                common.settings.endGroup()

        exportRefreshToken.triggered.connect(exportrt)

        def importrt():
            text, ok = QInputDialog.getText(
                None, "Insert refresh token", "Enter refresh token:"
            )

            if ok:
                # Not done in do refresh
                common.settings.beginGroup("account")
                res = do_refresh_from_token(self.auth, text)
                if res[0]:
                    self.infoDialog("Refresh token import", "Token valid")
                else:
                    self.infoDialog(
                        "Refresh token import",
                        "Internal error" if res[1] == 0 else "Token invalid",
                    )

        importRefreshToken.triggered.connect(importrt)

        # Get a button hight lower point
        button_pos = self.abutton.mapToGlobal(QPoint(0, self.abutton.height()))

        # Show the menu at the button's bottom-left corner
        menu.exec(button_pos)

    def __init__(self, auth):
        super().__init__()
        self.auth = auth
        self.resize(600, 300)
        self.setWindowTitle("Quickcraft")
        self.setContentsMargins(20, 20, 20, 20)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        common.initBackround(self)
        common.initLogo(self, layout, stretch=4)

        formGrid = QGridLayout()
        formGrid.setColumnStretch(0, 1)
        formGrid.setColumnStretch(1, 1)

        def mkText(text: str):
            label = common.ResizingTextLabel(text)
            label.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
            )
            label.label.setFont(QFont(common.families[0], 40))
            return label

        common.settings.beginGroup("account")
        slider = sliders.Switch(initial=common.settings.value("authEnabled"))
        common.settings.endGroup()

        def switchEnabled(checked):
            common.settings.beginGroup("account")
            common.settings.setValue("authEnabled", checked)
            common.settings.endGroup()

        slider.clicked.connect(switchEnabled)
        slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        formGrid.addWidget(mkText("Enable microsoft auth"), 0, 0)
        formGrid.addWidget(slider, 0, 1)
        layout.addLayout(formGrid, 1)

        # Login button
        self.loginButton = common.ResizingButton("Login")
        self.loginButton.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.loginButton.button.setFont(QFont(common.families[0], 80))
        self.loginButton.button.setStyleSheet(
            "background-color: green;border-radius:15px;"
        )
        self.loginButton.button.clicked.connect(self.login)
        layout.addWidget(self.loginButton, 2)

        self.abutton = common.ResizingButton("Advanced")
        self.abutton.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.abutton.button.setFont(QFont(common.families[0], 80))
        self.abutton.button.setStyleSheet("background-color: green;border-radius:15px;")
        self.abutton.button.clicked.connect(self.advanced)
        layout.addWidget(self.abutton, 2)

        info = authFlow(self.auth)
        if info[0]:
            self.mkPreview(info[1], layout.indexOf(self.loginButton))

    def closeEvent(self, event):
        super().closeEvent(event)
        if self.skinprev is not None:
            self.layout().removeWidget(self.skinprev)
            self.skinprev.deleteLater()
            self.skinprev.timer.stop()
        event.accept()
        self.closed.emit()
