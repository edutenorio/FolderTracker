# setup.py for FolderSync
import sys
import os
from cx_Freeze import setup, Executable

# Set environment variables for Tcl/Tk (important for Tkinter)
base = None
if sys.platform == "win32":
    os.environ["TCL_LIBRARY"] = r"D:\Users\edute\AppData\Local\Programs\Python\Python313\tcl\tcl8.6"
    os.environ["TK_LIBRARY"] = r"D:\Users\edute\AppData\Local\Programs\Python\Python313\tcl\tk8.6"
    base = "Win32GUI"  # No console window for Tkinter apps

# Include folders and files (icons, etc.)
include_files = [
    ("img", "img"),  # images used in the UI
    (os.environ["TCL_LIBRARY"], "tcl"),
    (os.environ["TK_LIBRARY"], "tk")
]

build_exe_options = {
    "packages": ["tkinter", "os", "dotenv", "PIL", "icecream"],
    "include_files": include_files,
    "include_msvcr": True
}

setup(
    name="FolderSync",
    version="1.0",
    description="Folder Sync utility",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base, target_name="FolderSync.exe", icon="img/icon2.ico")]
)
