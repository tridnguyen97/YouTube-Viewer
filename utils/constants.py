import sys, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, 
                        '_MEIPASS', 
                        os.path.dirname(BASE_DIR))
    return os.path.join(base_path, relative_path)


URL_FILE_DIR = resource_path("urls.txt")
PROXY_FILE_DIR = resource_path("proxy.txt")
MAINVIEW_DIR = resource_path("ui/MainView.glade")
SETTINGVIEW_DIR = resource_path("ui/SettingView.glade")
MENU_DIR = resource_path("ui/menu.xml")
BATCH_FILE_DIR = resource_path("killdrive.bat")
CONFIG_FILE_DIR = resource_path("config.json")
PATCHED_DRIVERS_DIR = resource_path("patched_drivers")
DRIVER_IDENTIFIER_DIR = resource_path(
    os.path.join("patched_drivers", "chromedriver")
)
DATABASE_DIR = resource_path("database.db")
DATABASE_BACKUP_DIR = resource_path("database_backup.db")
PROXY_TYPES = [
    "HTTP",
    "SOCKS4",
    "SOCKS5",
    "ALL"
]

HEADERS_1 = ['Worker', 'Video Title', 'Watch / Actual Duration']
HEADERS_2 = ['Index', 'Video Title', 'Views']

VIEWPORTS = ['2560,1440', '1920,1080', '1440,900',
             '1536,864', '1366,768', '1280,1024', '1024,768']

REFERERS = ['https://search.yahoo.com/', 
            'https://duckduckgo.com/', 'https://www.google.com/',
            'https://www.bing.com/', 'https://t.co/', '']
SCRIPT_VERSION = '1.8.0'

