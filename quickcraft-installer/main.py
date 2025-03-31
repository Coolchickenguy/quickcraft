import minecraft_launcher_lib
import subprocess
import uuid
import getpass
import hashlib
import os

ver = minecraft_launcher_lib.utils.get_latest_version()["release"]
hash=hashlib.sha1(getpass.getuser().encode()).hexdigest()
uname=hash[:12]
minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()
if (not os.path.exists(minecraft_directory)) or list(map(lambda x: x['id'],minecraft_launcher_lib.utils.get_installed_versions(minecraft_directory))).count(ver) == 0:
    print("INSTALLING " + ver)
    minecraft_launcher_lib.install.install_minecraft_version(ver, minecraft_directory)
print("STARTING " + ver)
options = {
    "username": uname,
    "uuid": hash[0:6] + "-" + hash[6:10] + "-" + hash[10:14] + "-" + hash[14:18] + "-" + hash[18:30],
    "token": "nevergonagiveyouup",
    #"executablePath": os.path.abspath("./java/bin/java")
}
minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(ver, minecraft_directory, options)

# Start Minecraft
subprocess.run(minecraft_command, cwd=minecraft_directory)