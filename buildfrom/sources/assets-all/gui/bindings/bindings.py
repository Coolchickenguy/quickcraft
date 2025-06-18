import minecraft_launcher_lib
import subprocess
import getpass
import hashlib
import os
import json
import minecraft_launcher_lib._helper
import sys
from minecraft_launcher_lib._internal_types.shared_types import ClientJson
from minecraft_launcher_lib.types import CallbackDict
minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()
def latest_ver():
    return minecraft_launcher_lib.utils.get_latest_version()["release"]

def installed(ver:str):
    return os.path.exists(minecraft_directory) and list(map(lambda x: x['id'],minecraft_launcher_lib.utils.get_installed_versions(minecraft_directory))).count(ver) != 0 and os.path.exists(os.path.join(minecraft_directory, "versions", ver, ver + ".jar"))

def install (ver:str,cbdict:CallbackDict | None = None):
    minecraft_launcher_lib.install.install_minecraft_version(versionid=ver, minecraft_directory=minecraft_directory, callback=cbdict)

def get_versiondata(ver:str):
    with open(os.path.join(minecraft_directory, "versions", ver, ver + ".json"), "r", encoding="utf-8") as f:
        data: ClientJson = json.load(f)

    if "inheritsFrom" in data:
        data = minecraft_launcher_lib._helper.inherit_json(data, minecraft_directory)
    return data

def install_mappings(ver:str,cbdict:CallbackDict | None = None):
    versiondata = get_versiondata(ver)
    if "downloads" in versiondata:
        if cbdict != None:
            cbdict["setMax"](1)
            cbdict["setProgress"](0)
        
        minecraft_launcher_lib._helper.download_file(versiondata["downloads"]["client_mappings"]["url"], os.path.join(minecraft_directory, "versions", versiondata["id"], versiondata["id"] + ".txt"), {} if cbdict == None else cbdict, sha1=versiondata["downloads"]["client_mappings"]["sha1"], minecraft_directory=minecraft_directory)
        if cbdict != None:
            cbdict["setProgress"](1)
            cbdict["setStatus"]("Installation complete")
    else:
        raise Exception("Mappings not found")

def whereis_mappings(ver:str):
    return os.path.join(minecraft_directory, "versions", ver, ver + ".txt")
def is_java_broken():
    return not os.path.exists(os.path.join(minecraft_directory,"runtime"))

def install_java_for_broken(ver:str):
    versiondata=get_versiondata(ver)
    if "javaVersion" in versiondata:
        minecraft_launcher_lib.runtime.install_jvm_runtime(versiondata["javaVersion"]["component"], minecraft_directory)

def gen_startvars():
    uname_hash=hashlib.sha1(getpass.getuser().encode()).hexdigest()
    uname=uname_hash[:12]
    uuid=uname_hash[0:6] + "-" + uname_hash[6:10] + "-" + uname_hash[10:14] + "-" + uname_hash[14:18] + "-" + uname_hash[18:30]
    return uname,uuid

def start(ver:str,uname,uuid,just_command:bool = False,access_token:str = None):
    options = {
        "username": uname,
        "uuid": uuid,
        "token": "nevergonagiveyouup" if access_token is None or access_token == "" else access_token,
    }
    minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(ver, minecraft_directory, options)
    if just_command:
        return minecraft_command
    # Start Minecraft
    return subprocess.Popen(minecraft_command, cwd=minecraft_directory).pid

def locate_java(ver:str):
    versiondata=get_versiondata(ver)
    if "javaVersion" in versiondata:
        java_path = minecraft_launcher_lib.runtime.get_executable_path(versiondata["javaVersion"]["component"], minecraft_directory)
        if java_path == None:
            install_java_for_broken(ver)
            return locate_java(ver)
        return java_path
def locate_java_sharedObject(ver:str):
    javaExecutable=locate_java(ver)
    if sys.platform == "win32":
        return os.path.join(os.path.dirname(javaExecutable),"server/jvm.dll")
    # Darwin (macos) and linux
    else:
        return os.path.join(os.path.dirname(os.path.dirname(javaExecutable)),"lib","server","libjvm.so")