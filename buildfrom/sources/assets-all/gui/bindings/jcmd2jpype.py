from typing import Any
import jpype
import threading
from .. import common
flaged=[False]
def parseJavaCommand(args: list[str]):
    i = 1
    grouped_args = {"jvm":[],"classpath":None,"mainclass":None,"program":[]}
    while i < len(args):
        arg = args[i]
        if arg.startswith("-X") or arg.startswith("-D") or arg == "-ea" or arg == "-esa":
            grouped_args["jvm"].append(arg)
        elif arg == "-cp" or arg == "-classpath":
            i += 1
            grouped_args["classpath"] = args[i]
        else:
            grouped_args["mainclass"] = arg
            grouped_args["program"] = args[i+1:]
            break
        i += 1
    return grouped_args
def startJvm(grouped_args:dict[str,Any],jvm_path:str):
    if jpype.isJVMStarted():
        raise Exception("Jvm is already running")
    jvmArgs = [jvm_path] + grouped_args["jvm"]
    if "classpath" in grouped_args and grouped_args["classpath"] != None:
        jpype.startJVM(*jvmArgs,classpath=grouped_args["classpath"])
    else:
        jpype.startJVM(*jvmArgs)
    """splitPackage=grouped_args["mainclass"].split(".")
    rootPackage=jpype.JPackage(splitPackage[0])
    packagePath=[rootPackage]
    for path in splitPackage[1:]:
        packagePath[0]=getattr(packagePath[0],path)
    package=packagePath[0]
    package(grouped_args["program"])"""
    mainClass=jpype.JClass(grouped_args["mainclass"])
    return common.TaskManager.startTask(threading.Thread(target=mainClass.main,args=[jpype.JArray(jpype.JString)(grouped_args["program"])]))