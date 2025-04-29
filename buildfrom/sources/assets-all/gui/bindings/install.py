from .. import common, _types
from . import bindings
import multiprocessing
from collections.abc import Callable
from PyQt6.QtCore import QTimer
timers = []
def qtThreadOrProcessMon(threadOrProcess:_types.ThreadOrProcess,callback:Callable[[],None]):
    timer = QTimer()
    def check():
        if not threadOrProcess.is_alive():
            timer.stop()
            threadOrProcess.join()
            callback()
    timer.timeout.connect(check)
    timer.start(200)
    timers.append(timer)

class install:
    max_progress = 0
    bdcpmInstance:common.TaskManagerClass.bidirectionalCrossProcessControlManager
    done:bool = False
    def install(self,version):
        print("installing " + str(version))
        import time
        last_run=[time.monotonic_ns()]
        min_sep = 200*1000000
        def throtle(func):
            def f(*args,**kwargs):
                if (last_run[0]+min_sep)<time.monotonic_ns():
                    func(*args,**kwargs)
                    last_run[0]=time.monotonic_ns()
            return f
        cbdict={"setStatus":throtle(self.bdcpmInstance.proxyOtherSideFunction("setStatus",False)),"setMax":self.bdcpmInstance.proxyOtherSideFunction("setMax",False),"setProgress":self.bdcpmInstance.proxyOtherSideFunction("setProgress",False)}
        bindings.install(ver=version,cbdict=cbdict)
        bindings.install_mappings(ver=version,cbdict=cbdict)

    def __init__(self,version,gui):
        print("Launching installer thread")
        self.bdcpmInstance = common.TaskManager.bidirectionalCrossProcessControlManager()
        self.installUuid = common.TaskManager.startTask(multiprocessing.Process(target=self.install,args=[version]),"minecraft",qtThreadOrProcessMon)
        self.bdcpmInstance.handleCalls(gui)
        def handeEnd(uuid:str):
            self.close()
        common.TaskManager.onEnd(self.installUuid,handeEnd)
    def kill(self):
        self.done = True
        if self.installUuid != None:
            common.TaskManager.kill(self.installUuid)
        if self.bdcpmInstance != None:
            self.bdcpmInstance.stopped = True
    def close(self):
        self.done = True
        if self.bdcpmInstance != None:
            self.bdcpmInstance.stopped = True
        if self.bdcpmInstance.on != None:
            try:
                self.bdcpmInstance.on().close()
                print("Installer finished")

            except Exception as e:
                print(e.with_traceback())
        
