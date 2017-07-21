import sys, os
from cx_Freeze import setup, Executable

base = "Win32GUI"

executables = [Executable("main.py", base=base)]

packages = ["vlc", "sys", "ctypes", "os", "functools", "inspect", "tkinter"]
options = {
    'build_exe': {
        'packages':packages,
        ''' 
        #Auto copy of the DLLs is not working
        #  at this time. You'll have to manually
        #  copy them from the directory below.
        'include_files': [
                r'C:\Program Files\Python36\DLLs\tk86t.dll',
                r'C:\Program Files\Python36\DLLs\tcl86t.dll'
        ], #'''
    },
}

os.environ['TCL_LIBRARY'] = r'C:\Program Files\Python36\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Program Files\Python36\tcl\tk8.6'

setup(
    name = "PanelView for IP cams",
    author = "Jack Butler",
    options = options,
    version = "1.0",
    description = 'A 4 panel view for IP cams.',
    executables = executables
)