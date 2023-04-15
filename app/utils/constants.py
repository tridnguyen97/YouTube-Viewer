import os

cur_dir = os.getcwd()

URL_FILE_DIR = os.path.join(cur_dir, "urls.txt")
PROXY_FILE_DIR = os.path.join(cur_dir, "proxy.txt")
PROXY_TYPES = [
    "HTTP",
    "SOCKS4",
    "SOCKS5",
    "ALL"
]