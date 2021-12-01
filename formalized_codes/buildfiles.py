import os

try:
    import PyInstaller
except:
    os.system("pip3 install pyinstaller")

try:
    import win32api
except:
    os.system("pip3 install pypiwin32")

try:
    import openpyxl
except:
    os.system("pip3 install openpyxl")

os.system("pyinstaller mainfile.py pisqpipe.py --name pbrain-xiaocilao.exe --onefile")
