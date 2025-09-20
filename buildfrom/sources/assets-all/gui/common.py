from multiprocessing.connection import Connection
import queue
from typing import Any, Union
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QSizePolicy,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtGui import QFontDatabase, QPixmap, QPalette, QBrush, QIcon, QFontMetrics
from PyQt6.QtCore import (
    Qt,
    QSize,
    pyqtSignal,
    QSettings,
    QTimer,
    QObject,
    QThread,
    pyqtSlot,
    QMetaObject,
    QCoreApplication,
)
import sys
import multiprocessing
import threading
import uuid
from collections.abc import Callable
from . import _types
import os
import weakref
import time
from assets_root import assets_root

app = QApplication(sys.argv)
app.setWindowIcon(QIcon(os.path.join(assets_root, "logo.ico")))
fontId = QFontDatabase.addApplicationFont(
    os.path.join(assets_root, "Comfortaa-VariableFont_wght.ttf")
)
if fontId < 0:
    print("Error")

families = QFontDatabase.applicationFontFamilies(fontId)

settings = QSettings("quickcraft", "quickcraftLauncher")


def keyOfValueDict(d, val):
    for k, v in d.items():
        if id(v) == id(val):
            return k
    return None


def initBackround(self):
    # Load the original image
    pixmap = QPixmap(os.path.join(assets_root, "dirt.jpg"))
    scaled = pixmap.scaled(50, 50)
    # Set the brush with the scaled pixmap to the background role
    palette = QPalette()
    palette.setBrush(QPalette.ColorRole.Window, QBrush(scaled))
    self.setPalette(palette)
    self.setAutoFillBackground(True)


class ResizablePixmapLabel(QLabel):
    def __init__(self, pixmap=None):
        super().__init__()
        self._pixmap = None
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if pixmap:
            self.setPixmap(pixmap)

    def setPixmap(self, pixmap: QPixmap):
        self._pixmap = pixmap
        self.updatePixmap()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updatePixmap()

    def updatePixmap(self):
        if not self._pixmap:
            return

        label_size = self.size()
        pixmap_size = self._pixmap.size()

        # Calculate scaling ratio
        width_ratio = label_size.width() / pixmap_size.width()
        height_ratio = label_size.height() / pixmap_size.height()
        scale_ratio = min(width_ratio, height_ratio)

        new_size = QSize(
            int(pixmap_size.width() * scale_ratio),
            int(pixmap_size.height() * scale_ratio),
        )

        scaled_pixmap = self._pixmap.scaled(
            new_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        super().setPixmap(scaled_pixmap)

    def minimumSizeHint(self):
        return QSize(0, 0)  # Let the window shrink freely


class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class ResizableClickableLabel(ResizablePixmapLabel):
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


def __adjustFontSize__(self, rect):
    if not self.text():
        return
    # rect = self.contentsRect()
    if rect.isEmpty():
        return
    text = self.text()
    font = self.font()
    font_size = max(1, font.pointSize())
    font.setPointSize(font_size)
    fm = QFontMetrics(font)
    bounding = fm.boundingRect(rect, Qt.TextFlag.TextSingleLine, text)
    # If the bounding font box is smaller on BOTH x and y than the rect, try increasing
    if bounding.width() <= rect.width() and bounding.height() <= rect.height():
        # Try increasing font size until it doesn't fit
        while True:
            font_size += 1
            font.setPointSize(font_size)
            fm = QFontMetrics(font)
            bounding = fm.boundingRect(rect, Qt.TextFlag.TextSingleLine, text)
            # If the font's bounding rect is bigger than the content rect in one or two directions, decrease font size by one and break
            if bounding.width() >= rect.width() or bounding.height() >= rect.height():
                font_size -= 1
                break
    else:
        # Decrease font size until it fits
        while font_size > 1:
            font_size -= 1
            font.setPointSize(font_size)
            fm = QFontMetrics(font)
            bounding = fm.boundingRect(rect, Qt.TextFlag.TextSingleLine, text)
            # When the new font size is smaller or equal to the content rect, break
            if bounding.width() <= rect.width() and bounding.height() <= rect.height():
                break
    font.setPointSize(font_size)
    self.setFont(font)


class __ResizingButton__(QPushButton):
    textChanged = pyqtSignal()

    def __init__(self, text):
        super().__init__(text)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setStyleSheet("text-align: center;")

    def minimumSizeHint(self):
        return QSize(0, 0)
    
    def setText(self, text: str):
        if text != self.text():
            super().setText(text)
            self.textChanged.emit()


class ResizingButton(QWidget):
    button: __ResizingButton__

    def __init__(self, text=""):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.button = __ResizingButton__(text)
        layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.qlayout = layout
        self.button.textChanged.connect(self.adjustContentsText)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjustContentsText()

    def adjustContentsText(self):
        __adjustFontSize__(self.button, self.contentsRect())

    def minimumSizeHint(self):
        return QSize(0, 0)


class __ResizingTextLabel__(QLabel):
    textChanged = pyqtSignal()

    def __init__(self, text):
        super().__init__(text)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setStyleSheet("text-align: center;")

    def minimumSizeHint(self):
        return QSize(0, 0)
    
    def setText(self, text: str):
        if text != self.text():
            super().setText(text)
            self.textChanged.emit()


class ResizingTextLabel(QWidget):
    label: __ResizingTextLabel__

    def __init__(self, text=""):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.label = __ResizingTextLabel__(text)
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.qlayout = layout
        self.label.textChanged.connect(self.adjustContentsText)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjustContentsText()

    def adjustContentsText(self):
        __adjustFontSize__(self.label, self.contentsRect())

    def minimumSizeHint(self):
        return QSize(0, 0)


def initLogo(self, layout, stretch=0):
    pixmap = QPixmap(os.path.join(assets_root, "logo_full.png"))
    label = ResizablePixmapLabel(pixmap)
    label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    layout.addWidget(label, stretch=stretch)


winmanInstanceCount = [0]


class WinManClass:
    _windows: dict[Any, Callable[[], None]] = {}
    id = 0

    def __init__(self):
        if winmanInstanceCount[0] != 0:
            raise IndexError(
                "Only one WinManClass may exsist, please use the shared common.WinMan instance insted (No real code reason, this is just to keep things tidy)"
            )
        winmanInstanceCount[0] += 1

    def add(self, window):
        id = self.id
        self._windows[window] = []
        self.id += 1
        print("Winman is holding window id " + str(id))

        def onClosed():
            window.closed.disconnect(onClosed)
            print("Winman is releasing window id " + str(id))
            for listener in self._windows.pop(window):
                listener()

        window.closed.connect(onClosed)

    def onClose(self, window, listener):
        self._windows[window].append(listener)


WinMan = WinManClass()

TaskManagerInstanceCount = [0]

timers = []


def qtThreadOrProcessMon(
    threadOrProcess: _types.ThreadOrProcess, callback: Callable[[], None]
):
    timer = QTimer()

    def check():
        if not threadOrProcess.is_alive():
            timer.stop()
            timers.remove(timer)
            threadOrProcess.join()
            callback()

    timer.timeout.connect(check)
    timer.start(200)
    timers.append(timer)


class MainThreadInvoker(QObject):
    _instance = None

    # Signal carrying a callable to invoke
    invoke_signal = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.invoke_signal.connect(self._invoke)

    @staticmethod
    def instance():
        if MainThreadInvoker._instance is None:
            MainThreadInvoker._instance = MainThreadInvoker()
        return MainThreadInvoker._instance

    def _invoke(self, func):
        try:
            func()
        except Exception as e:
            print(f"Exception in invoked function: {e}")


MainThreadInvoker.instance()


class TaskManagerClass:
    """A manager for threads and processes that allows grouping to prevent parallel execution of groups of tasks.

    Represents the tasks by UUIDs so it is easy to control them without leaking memory.

    (At least, all the memory you can leak is dangling pointers, nothing worse than that unless you REALY mess up.)

    Raises:
        IndexError: More than one of this class has been created
        Exception: The task can not be killed
    Returns:
        _type_: _description_
    """

    _groups: dict[str, list[str]] = {}

    _uuidMap: dict[str, _types.ThreadOrProcess] = {}
    _uuidStartHandlersMap: dict[str, list[Callable[[str], _types.ThreadOrProcess]]] = {}
    _uuidEndHandlersMap: dict[str, list[Callable[[str], _types.ThreadOrProcess]]] = {}
    _monMap: dict[str, Callable[[_types.ThreadOrProcess, Callable[[], None]], None]] = (
        {}
    )

    def __init__(self) -> None:
        if TaskManagerInstanceCount[0] != 0:
            raise IndexError(
                "Only one TaskManagerClass may exsist, please use the shared common.TaskManager instance insted (No real code reason, this is just to keep things tidy)"
            )
        TaskManagerInstanceCount[0] += 1
        # Some debugging code
        """def logs():
            while True:
                print(self._uuidMap)
                time.sleep(2.5)
        threading.Thread(target=logs,daemon=True).start()"""

    def startTaskUuid(self, taskUuid: str, groupName: str | None = None) -> str:
        """Start a task by it's uuid, please use startTask instead.

        Args:
            taskUuid (str): The uuid of the task
            groupName (str | None, optional): See startTask. Defaults to None.

        Returns:
            str: The uuid of the task
        """
        task = self._uuidMap[taskUuid]
        if groupName != None:
            if not groupName in self._groups:
                self._groups[groupName] = []
            self._groups[groupName].append(taskUuid)

        def preCallbacks(taskUuid: str):
            if taskUuid in self._uuidStartHandlersMap:
                for callback in self._uuidStartHandlersMap.pop(taskUuid):
                    try:
                        callback(taskUuid)
                    except Exception as e:
                        print(f"A callback had an error {e}")

        def callbacks(taskUuid: str):
            if taskUuid in self._uuidEndHandlersMap:
                for callback in self._uuidEndHandlersMap.pop(taskUuid):
                    try:
                        callback(taskUuid)
                    except Exception as e:
                        print(f"A callback had an error {e}")

        # One meaning we are the only task
        if groupName == None or len(self._groups[groupName]) == 1:
            preCallbacks(taskUuid)
            task.start()

            def onEnd(task: _types.ThreadOrProcess):
                taskUuid = keyOfValueDict(self._uuidMap, task)

                def cb():
                    callbacks(taskUuid)
                    self._uuidMap.pop(taskUuid)
                    if taskUuid in self._monMap:
                        self._monMap.pop(taskUuid)
                    # This is ok because the groupName will stay constant
                    if groupName != None:
                        self._groups[groupName].remove(taskUuid)
                        if len(self._groups[groupName]) != 0:
                            newTaskUuid = self._groups[groupName][0]
                            newTask = self._uuidMap[newTaskUuid]
                            newTask.start()
                            preCallbacks(newTaskUuid)
                            onEnd(newTask)

                if taskUuid in self._monMap:
                    self._monMap[taskUuid](task, cb)
                else:

                    def endMon():
                        task.join()
                        cb()

                    threading.Thread(target=endMon, daemon=True).start()

            onEnd(task)
            return taskUuid

    def startTask(
        self,
        task: _types.ThreadOrProcess,
        groupName: str | None = None,
        mon: Callable[[_types.ThreadOrProcess, Callable[[], None]], None] | None = None,
    ) -> str:
        """Start and manage a task

        Args:
            task (_types.ThreadOrProcess): The task to manage
            groupName (str | None, optional): The optional non-overlap group, if provided and there a task running, it goes at the end of a queue that runs the next after the current one running finishes. Defaults to None.
            mon (Callable[[_types.ThreadOrProcess,Callable[[],None]],None]|None): The ThreadOrProcess monitor. Defaults to None.

        Returns:
            str: The uuid of the task, can be used to manage it.
        """
        taskUuid = uuid.uuid4().hex
        self._uuidMap[taskUuid] = task
        if mon != None:
            self._monMap[taskUuid] = mon
        self.startTaskUuid(taskUuid, groupName)
        return taskUuid

    def kill(self, taskUuid: str) -> None:
        """Kill a task managed by this class by uuid

        Args:
            taskUuid (str): The uuid of the task

        Raises:
            Exception: If the task does not have the terminate property
        """
        if taskUuid in self._uuidMap:
            task = self._uuidMap[taskUuid]
            if not hasattr(task, "kill"):
                raise Exception("Can not kill a " + str(type(task)))
            if task.is_alive():
                task.kill()

    def onStart(self, taskUuid: str, callback: Callable[[str], None]) -> None:
        """Calls a callback once a task starts running

        Args:
            taskUuid (str): The task's uuid
            callback (Callable[[str],None]): The callback function, called with the one argurement being the task's uuid
        """
        if self.exsists(taskUuid):
            if self._uuidMap[taskUuid].is_alive():
                callback(taskUuid)
                return
            if taskUuid in self._uuidStartHandlersMap.keys():
                self._uuidStartHandlersMap[taskUuid].append(callback)
            else:
                self._uuidStartHandlersMap[taskUuid] = [callback]
        else:
            raise Exception(f"Task uuid {taskUuid} does not exsist")

    def onEnd(self, taskUuid: str, callback: Callable[[str], None]) -> None:
        """Calls a callback once a task finishes running

        Args:
            taskUuid (str): The task's uuid
            callback (Callable[[str],None]): The callback function, called with the one argurement being the task's uuid
        """
        if self.exsists(taskUuid):
            if taskUuid in self._uuidEndHandlersMap.keys():
                self._uuidEndHandlersMap[taskUuid].append(callback)
            else:
                self._uuidEndHandlersMap[taskUuid] = [callback]
        else:
            raise Exception(f"Task uuid {taskUuid} does not exsist")

    def exsists(self, taskUuid: str) -> bool:
        """Check if a task uuid exsists

        Args:
            taskUuid (str): The task's uuid
        Returns:
            bool: If the task exsists or not
        """
        return taskUuid in self._uuidMap

    # Common communication utils

    class bidirectionalCrossProcessControlManager:
        stopped: bool = False
        pipe: Union[tuple[Connection, Connection], tuple[queue.Queue, queue.Queue]]

        handlerUuid: str = None
        on = None
        _mainPid: int
        _origionalThread: str
        isThread: bool
        responces: dict[str, dict[str, Any]] = {}

        def __init__(self, isThread=False):
            self.pipe = (
                [queue.Queue(), queue.Queue()] if isThread else multiprocessing.Pipe()
            )
            self._mainPid = os.getpid()
            self._origionalThread = threading.current_thread().name
            self.isThread = isThread

        def _isMain(self):
            return (
                (threading.current_thread().name is self._origionalThread)
                if self.isThread
                else (self._mainPid == os.getpid())
            )

        def _controlHandler(
            self,
        ):
            pipe = self.pipe[0] if self._isMain() else self.pipe[1]
            sendFunc = pipe.put if self.isThread else pipe.send
            while not self.stopped and self.on is not None:
                try:

                    def run(controlmsg):
                        if controlmsg["action"] == "invoke":
                            func = getattr(self.on(), controlmsg["method"])

                            def reply(out):
                                sendFunc(
                                    {
                                        "action": "recv",
                                        "uuid": controlmsg["uuid"],
                                        "data": out,
                                    }
                                )

                            def wrapper():
                                try:
                                    out = func(
                                        *controlmsg["args"], **controlmsg["kwargs"]
                                    )
                                    if controlmsg["return"]:
                                        reply(out)
                                except Exception as e:
                                    print(f"Exception: {e}")

                            if controlmsg["qtMainThreadify"]:
                                MainThreadInvoker.instance().invoke_signal.emit(wrapper)
                            else:
                                wrapper()
                        elif controlmsg["action"] == "get":
                            sendFunc(
                                {
                                    "action": "recv",
                                    "uuid": controlmsg["uuid"],
                                    "data": getattr(self.on(), controlmsg["prop"]),
                                }
                            )
                        elif controlmsg["action"] == "set":
                            setattr(self.on(), controlmsg["prop"], controlmsg["value"])
                        elif controlmsg["action"] == "recv":
                            self.responces[controlmsg["uuid"]] = controlmsg

                    if self.isThread:
                        try:
                            run(pipe.get_nowait())
                        except queue.Empty:
                            pass
                    elif pipe.poll(2):
                        run(pipe.recv())
                except Exception as e:
                    print(e)
                else:
                    continue
            if self.isThread:
                self.pipe[0].closed = True
                self.pipe[1].closed = True
            else:
                self.pipe[0].close()
                self.pipe[1].close()

        def __del__(self):
            if self.pipe[0].closed == False:
                if self.isThread:
                    self.pipe[0].closed = True
                else:
                    self.pipe[0].close()
            if self.pipe[1].closed == False:
                if self.isThread:
                    self.pipe[1].closed = True
                else:
                    self.pipe[1].close()

        def proxyOtherSideFunction(
            self, name: str, doReturn: bool = True, qtMainThreadify: bool = False
        ):
            pipe = self.pipe[0] if self._isMain() else self.pipe[1]
            sendFunc = pipe.put if self.isThread else pipe.send

            def func(*args, **kwargs):
                msguuid = uuid.uuid4()
                sendFunc(
                    {
                        "action": "invoke",
                        "method": name,
                        "args": args,
                        "kwargs": kwargs,
                        "uuid": msguuid,
                        "return": doReturn,
                        "qtMainThreadify": qtMainThreadify,
                    }
                )
                if doReturn:
                    while not msguuid in self.responces:
                        time.sleep(0.01)

                    res = self.responces.pop(msguuid)
                    return res["data"]

            return func

        def get(self, key):
            pipe = self.pipe[0] if self._isMain() else self.pipe[1]
            sendFunc = pipe.put if self.isThread else pipe.send
            msguuid = uuid.uuid4()
            sendFunc({"action": "get", "prop": key, "uuid": msguuid})
            while not msguuid in self.responces:
                pass

            res = self.responces.pop(msguuid)
            return res["data"]

        def set(self, key, value):
            pipe = self.pipe[0] if self._isMain() else self.pipe[1]
            sendFunc = pipe.put if self.isThread else pipe.send
            msguuid = uuid.uuid4()
            sendFunc({"action": "set", "prop": key, "value": value, "uuid": msguuid})

        def handleCalls(self, on) -> bool:
            """Start a thread to handle all control calls

            Returns:
                bool: If it actualy started (false means that the thread already exsists)
            """
            if self.handlerUuid == None or not TaskManager.exsists(self.handlerUuid):
                self.on = weakref.ref(on)

                thread = threading.Thread(target=self._controlHandler, daemon=True)
                self.handlerUuid = TaskManager.startTask(thread)

                def onEnd(uuid: str):
                    self.handlerUuid = None

                TaskManager.onEnd(self.handlerUuid, onEnd)
                return True
            else:
                return False


TaskManager = TaskManagerClass()
