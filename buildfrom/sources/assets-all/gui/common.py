from multiprocessing.connection import Connection
from typing import Any
from PyQt6.QtWidgets import QApplication, QLabel, QSizePolicy
from PyQt6.QtGui import QFontDatabase, QPixmap, QPalette, QBrush, QIcon
from PyQt6.QtCore import Qt, QSize
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
app.setWindowIcon(QIcon(os.path.join(assets_root,"logo.ico")))
fontId = QFontDatabase.addApplicationFont(os.path.join(assets_root,"Comfortaa-VariableFont_wght.ttf"))
if fontId < 0: print("Error")
 
families = QFontDatabase.applicationFontFamilies(fontId)

def keyOfValueDict(d, val):
    for k, v in d.items():
        if id(v) == id(val):
            return k
    return None

def initBackround(self):
    # Load the original image
    pixmap = QPixmap(os.path.join(assets_root,"dirt.jpg"))
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
            int(pixmap_size.height() * scale_ratio)
        )

        scaled_pixmap = self._pixmap.scaled(
            new_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        super().setPixmap(scaled_pixmap)
    
    def minimumSizeHint(self):
        return QSize(0, 0)  # Let the window shrink freely


def initLogo(self,layout):
    pixmap = QPixmap(os.path.join(assets_root,"logo_full.png"))
    label =  ResizablePixmapLabel(pixmap)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(label)

winmanInstanceCount = [0]

class WinManClass:
    _windows:dict[Any,Callable[[],None]] = {}
    id = 0
    def __init__(self):
        if winmanInstanceCount[0] != 0:
            raise IndexError("Only one WinManClass may exsist, please use the shared common.WinMan instance insted (No real code reason, this is just to keep things tidy)")
        winmanInstanceCount[0] += 1
    def add(self,window):
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

    def onClose(self,window,listener):
        self._windows[window].append(listener)

WinMan = WinManClass()

TaskManagerInstanceCount = [0]
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
    _groups:dict[str,list[str]] = {}

    _uuidMap:dict[str,_types.ThreadOrProcess] = {}
    _uuidStartHandlersMap:dict[str,list[Callable[[str],_types.ThreadOrProcess]]] = {}
    _uuidEndHandlersMap:dict[str,list[Callable[[str],_types.ThreadOrProcess]]] = {}
    _monMap:dict[str,Callable[[_types.ThreadOrProcess,Callable[[],None]],None]] = {}

    def __init__(self) -> None:
        if TaskManagerInstanceCount[0] != 0:
            raise IndexError("Only one TaskManagerClass may exsist, please use the shared common.TaskManager instance insted (No real code reason, this is just to keep things tidy)")
        TaskManagerInstanceCount[0] += 1
        # Some debugging code
        """def logs():
            while True:
                print(self._uuidMap)
                time.sleep(2.5)
        threading.Thread(target=logs,daemon=True).start()"""

    def startTaskUuid(self,taskUuid:str,groupName:str|None = None) -> str:
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
        def preCallbacks(taskUuid:str):
            if taskUuid in self._uuidStartHandlersMap:
                for callback in self._uuidStartHandlersMap.pop(taskUuid):
                    try:
                        callback(taskUuid)
                    except Exception as e:
                        print(f"A callback had an error {e}")
        def callbacks(taskUuid:str):
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
            def onEnd(task:_types.ThreadOrProcess):
                taskUuid=keyOfValueDict(self._uuidMap,task)
                def cb():
                    callbacks(taskUuid)
                    self._uuidMap.pop(taskUuid)
                    if taskUuid in self._monMap:
                        self._monMap.pop(taskUuid)
                    # This is ok because the groupName will stay constant
                    if groupName != None:
                        self._groups[groupName].remove(taskUuid)
                        if len(self._groups[groupName]) != 0:
                            newTaskUuid=self._groups[groupName][0]
                            newTask=self._uuidMap[newTaskUuid]
                            newTask.start()
                            preCallbacks(newTaskUuid)
                            onEnd(newTask)

                if taskUuid in self._monMap:
                    self._monMap[taskUuid](task,cb)
                else:
                    def endMon():
                        task.join()
                        cb()
                    threading.Thread(target=endMon,daemon=True).start()

            onEnd(task)
            return taskUuid
        
    def startTask(self,task:_types.ThreadOrProcess,groupName:str|None = None,mon:Callable[[_types.ThreadOrProcess,Callable[[],None]],None]|None = None) -> str:
        """Start and manage a task

        Args:
            task (_types.ThreadOrProcess): The task to manage
            groupName (str | None, optional): The optional non-overlap group, if provided and there a task running, it goes at the end of a queue that runs the next after the current one running finishes. Defaults to None.
            mon (Callable[[_types.ThreadOrProcess,Callable[[],None]],None]|None): The ThreadOrProcess monitor. Defaults to None.

        Returns:
            str: The uuid of the task, can be used to manage it.
        """
        taskUuid=uuid.uuid4().hex
        self._uuidMap[taskUuid] = task
        if mon != None:
            self._monMap[taskUuid] = mon
        self.startTaskUuid(taskUuid,groupName)
        return taskUuid

    def kill(self,taskUuid:str) -> None:
        """Kill a task managed by this class by uuid

        Args:
            taskUuid (str): The uuid of the task

        Raises:
            Exception: If the task does not have the terminate property
        """
        if taskUuid in self._uuidMap:
            task = self._uuidMap[taskUuid]
            if not hasattr(task,"kill"):
                raise Exception("Can not kill a " + str(type(task)))
            if task.is_alive():
                task.kill()

    def onStart(self,taskUuid:str,callback:Callable[[str],None]) -> None:
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
    def onEnd(self,taskUuid:str,callback:Callable[[str],None]) -> None:
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
    
    def exsists(self,taskUuid:str) -> bool:
        """Check if a task uuid exsists

        Args:
            taskUuid (str): The task's uuid
        Returns:
            bool: If the task exsists or not
        """
        return taskUuid in self._uuidMap
    
    # Common communication utils

    class bidirectionalCrossProcessControlManager:
        stopped:bool = False
        pipe:tuple[Connection, Connection]

        handlerUuid:str = None
        on = None
        _mainPid:int
        responces:dict[str,dict[str,Any]] = {}
        def __init__(self):
            self.pipe = multiprocessing.Pipe()
            self._mainPid = os.getpid()

        def _controlHandler(self,):
            pipe=self.pipe[0] if self._mainPid==os.getpid() else self.pipe[1]
            while not self.stopped and self.on is not None:
                try:
                    if pipe.poll(2):
                        controlmsg = pipe.recv()
                        if controlmsg["action"] == "invoke":
                            out = getattr(self.on(),controlmsg["method"])(*controlmsg["args"],**controlmsg["kwargs"])
                            if controlmsg["return"]:
                                pipe.send({"action":"recv","uuid":controlmsg["uuid"],"data":out})
                        elif controlmsg["action"] == "get":
                            pipe.send({"action":"recv","uuid":controlmsg["uuid"],"data":getattr(self.on(),controlmsg["prop"])})
                        elif controlmsg["action"] == "set":
                            setattr(self.on(),controlmsg["prop"],controlmsg["value"])
                        elif controlmsg["action"] == "recv":
                            self.responces[controlmsg["uuid"]] = controlmsg
                    else:
                        continue
                except Exception as e:
                    print(e)
            self.pipe[0].close()
            self.pipe[1].close()
        def __del__(self):
            if self.pipe[0].closed == False:
                self.pipe[0].close()
            if self.pipe[1].closed == False:
                self.pipe[1].close()
        def proxyOtherSideFunction(self,name:str,doReturn:bool = True):
            pipe=self.pipe[0] if self._mainPid==os.getpid() else self.pipe[1]
            def func(*args,**kwargs):
                msguuid=uuid.uuid4()
                pipe.send({"action":"invoke","method":name,"args":args,"kwargs":kwargs,"uuid":msguuid,"return":doReturn})
                if doReturn:
                    while not msguuid in self.responces:
                        time.sleep(0.01)

                    res=self.responces.pop(msguuid)
                    return res["data"]
            return func
        
        def get(self,key):
            pipe=self.pipe[0] if self._mainPid==os.getpid() else self.pipe[1]
            msguuid=uuid.uuid4()
            pipe.send({"action":"get","prop":key,"uuid":msguuid})
            while not msguuid in self.responces:
                pass

            res=self.responces.pop(msguuid)
            return res["data"]

        def set(self,key,value):
            pipe=self.pipe[0] if self._mainPid==os.getpid() else self.pipe[1]
            msguuid=uuid.uuid4()
            pipe.send({"action":"set","prop":key,"value":value,"uuid":msguuid})
        
        def handleCalls(self,on) -> bool:
            """Start a thread to handle all control calls

            Returns:
                bool: If it actualy started (false means that the thread already exsists)
            """
            if self.handlerUuid == None or not TaskManager.exsists(self.handlerUuid):
                self.on = weakref.ref(on)

                thread = threading.Thread(target=self._controlHandler,daemon=True)
                self.handlerUuid = TaskManager.startTask(thread)
                def onEnd(uuid:str):
                    self.handlerUuid = None
                TaskManager.onEnd(self.handlerUuid,onEnd)
                return True
            else:
                return False

TaskManager = TaskManagerClass()