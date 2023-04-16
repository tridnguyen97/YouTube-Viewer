import os
from pathlib import Path

cur_abs_path = Path(os.path.abspath(__file__))

BASE_DIR = cur_abs_path.parents[2]
URL_FILE_DIR = os.path.join(BASE_DIR, "urls.txt")
PROXY_FILE_DIR = os.path.join(BASE_DIR, "proxy.txt")
MAINVIEW_DIR = os.path.join(BASE_DIR, "app/ui/MainView.glade")
SETTINGVIEW_DIR = os.path.join(BASE_DIR, "app/ui/SettingView.glade")
PROXY_TYPES = [
    "HTTP",
    "SOCKS4",
    "SOCKS5",
    "ALL"
]