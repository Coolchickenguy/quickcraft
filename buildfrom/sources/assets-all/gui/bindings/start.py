from collections.abc import Callable
import os
from typing import Any
from .. import common
from . import bindings, install, proguard_parse, jcmd2jpype
import multiprocessing
from assets_root import assets_root
import os
import sys
class start:

    startProcessUuid:str
    bdcpmInstance:common.TaskManagerClass.bidirectionalCrossProcessControlManager
    mcPid:int 

    def start(self):
        print("Minecraft starting")
        try:
            uname, uuid = bindings.gen_startvars()
            #self.bdcpmInstance.set("mcPid",bindings.start(ver=bindings.latest_ver(),uname=uname,uuid=uuid))
            ver = bindings.latest_ver()
            if bindings.is_java_broken():
                bindings.install_java_for_broken(ver)
            if not os.path.exists(bindings.whereis_mappings(ver)):
                bindings.install_mappings(ver)

            # Start generating jni junk
            indexed:dict[str,Any] = proguard_parse.parse_proguard_mapping(bindings.whereis_mappings(ver))

            for key in indexed.keys():
                if indexed[key]["original_name"] == "com.mojang.blaze3d.platform.Window":
                    resultKey = key
                    break
            # END

            command = bindings.start(ver=ver,uname=uname,uuid=uuid,just_command=True)
            parsed=jcmd2jpype.parseJavaCommand(command[1:])
            parsed["jvm"].append(f"-javaagent:{os.path.join(assets_root,'quickcraft-agent.jar')}")
            parsed["jvm"].append(f"-DhookedClass={resultKey}")
            os.chdir(bindings.minecraft_directory)
            if sys.platform == "win32":
                jdir = os.path.dirname(bindings.locate_java(ver))
                os.environ["PATH"] = (jdir + ";" + os.path.join(jdir,"bin") + ";" + os.environ["PATH"])
            import jpype
            jcmd2jpype.startJvm(parsed,bindings.locate_java_sharedObject(ver))
            hooksClass = jpype.JClass("com.quickcraft.hook.hooks")
            this = self
            @jpype.JImplements('java.lang.Runnable')
            class OnWindowOpen:
                def __init__(self):
                    pass
                @jpype.JOverride
                def run(self):
                    this.closeGuiLoadingWindow()
            hooksClass.addListener(jpype.JString("onWindowCreated"),OnWindowOpen())
            #self.bdcpmInstance.proxyOtherSideFunction("hide",False)()
        except Exception as e:
            print(e)
    def closeGuiLoadingWindow(self):
        self.bdcpmInstance.set("minecraftOpened",True)
    def __init__(self,gui,onMcClose):
        gui.startInst = self
        self.bdcpmInstance = common.TaskManager.bidirectionalCrossProcessControlManager()

        self.startProcessUuid = common.TaskManager.startTask(multiprocessing.Process(target=self.start),"minecraft",install.qtThreadOrProcessMon)
        print(common.TaskManager._groups)
        common.TaskManager.onStart(self.startProcessUuid,lambda uuid: self.bdcpmInstance.handleCalls(gui))
        common.TaskManager.onEnd(self.startProcessUuid,lambda uuid: onMcClose())


    def close(self):
        common.TaskManager.kill(self.startProcessUuid)
        if hasattr(self,"mcPid"):
            os.kill(self.mcPid)
        print("Force killing minecraft")
        self.bdcpmInstance.stopped = True
