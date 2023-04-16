import sys, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(BASE_DIR))
    return os.path.join(base_path, relative_path)


URL_FILE_DIR = resource_path("urls.txt")
PROXY_FILE_DIR = resource_path("proxy.txt")
MAINVIEW_DIR = resource_path("ui/MainView.glade")
SETTINGVIEW_DIR = resource_path("ui/SettingView.glade")
MENU_DIR = resource_path("ui/menu.xml")
BATCH_FILE_DIR = resource_path("killdrive.bat")
PROXY_TYPES = [
    "HTTP",
    "SOCKS4",
    "SOCKS5",
    "ALL"
]