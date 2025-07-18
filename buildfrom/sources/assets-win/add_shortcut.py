import os
from win32com.client import Dispatch # type: ignore

def create_shortcut(path, target, working_dir=None, arguments="", icon_location=""):
    """
    Creates a Windows shortcut (.lnk) file.

    Args:
        path (str): Path to save the shortcut (e.g., "C:\\path\\to\\shortcut.lnk").
        target (str): Path to the target file or folder.
        working_dir (str, optional): Working directory for the shortcut. Defaults to None.
        arguments (str, optional): Arguments to pass to the target. Defaults to "".
        icon_location (str, optional): The location of the icon for the shortcut. Defaults to "". (Meaning it will resolve to the icon of the target)
    """
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = working_dir if working_dir else os.path.dirname(target)
    shortcut.Arguments = arguments
    if icon_location != "":
        shortcut.IconLocation = icon_location
    shortcut.save()

def get_desktop_path():
    # Create a shell object
    shell = Dispatch("WScript.Shell")
    # Get the Desktop path using the known folder constant
    desktop_dir = shell.SpecialFolders("Desktop")
    return desktop_dir

if __name__ == '__main__':
    shortcut_path = os.path.join(get_desktop_path(),"quickcraft.lnk")
    target_path = "powershell"
    create_shortcut(shortcut_path, target_path, working_dir=os.path.realpath("./"), arguments="-ExecutionPolicy Bypass -File ./start.ps1", icon_location=os.path.realpath("./logo.ico"))
    print(f"Shortcut created at: {os.path.abspath(shortcut_path)}")