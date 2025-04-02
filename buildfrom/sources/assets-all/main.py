import minecraft_launcher_lib
import subprocess
import getpass
import hashlib
import os
import json

ver = minecraft_launcher_lib.utils.get_latest_version()["release"]
hash=hashlib.sha1(getpass.getuser().encode()).hexdigest()
uname=hash[:12]
minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()
if (not os.path.exists(minecraft_directory)) or list(map(lambda x: x['id'],minecraft_launcher_lib.utils.get_installed_versions(minecraft_directory))).count(ver) == 0:
    print("INSTALLING " + ver)
    minecraft_launcher_lib.install.install_minecraft_version(ver, minecraft_directory)

if not os.path.exists(os.path.join(minecraft_directory,"runtime")):
    print("Downloading java (You probibly have the offical minecraft launcher and it did not install java to the path we use [your saves will still be here])")
    with open(os.path.join(minecraft_directory, "versions", ver, ver + ".json"), "r", encoding="utf-8") as f:
        versiondata = json.load(f)
        if "javaVersion" in versiondata:
            minecraft_launcher_lib.runtime.install_jvm_runtime(versiondata["javaVersion"]["component"], minecraft_directory)

print("STARTING " + ver)
options = {
    "username": uname,
    "uuid": hash[0:6] + "-" + hash[6:10] + "-" + hash[10:14] + "-" + hash[14:18] + "-" + hash[18:30],
    "token": "nevergonagiveyouup",
}
minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(ver, minecraft_directory, options)

# Start Minecraft
subprocess.run(minecraft_command, cwd=minecraft_directory)