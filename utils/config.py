import json
from utils.constants import CONFIG_FILE_DIR

def get_config() -> dict:
    try:
        with open(CONFIG_FILE_DIR, 'r', encoding='utf-8-sig') as f:
            config_list = f.read()
            config = json.loads(config_list)
        return config
    except Exception as e:
        print(e)


def config_api(config, enabled=True, port=5000):
    config["http_api"] = {
        "enabled": enabled,
        "host": "0.0.0.0",
        "port": port
    }
    return config

def config_database(config, is_database_stored=True):
    config["database"] = is_database_stored
    return config

def config_views(config, views=1000):
    try:
        config["views"] = int(views)
    except Exception:
        config["views"] = 100
    return config


def config_min_max(config, minimum=85, maximum=95):
    try:
        minimum = float(minimum)
    except Exception:
        minimum = 85.0
    try:
        maximum = float(maximum)
    except Exception:
        maximum = 95.0

    if minimum >= maximum:
        minimum = maximum - 5

    config["minimum"] = minimum
    config["maximum"] = maximum
    return config

def config_free_proxy(category, url_file, proxy_type, handle_proxy='y'):
    auth_required = False
    proxy_api = False

    if handle_proxy == 'y' or handle_proxy == 'yes':
        proxy_type = False
        filename = False

    else:
        if 'http://' in url_file or 'https://' in url_file:
            proxy_api = True

        if proxy_type not in ['HTTP', 'SOCKS4', 'SOCKS5', 'ALL']:
            raise Exception(
                '\nPlease input 1 for HTTP, 2 for SOCKS4, 3 for SOCKS5 and 4 for ALL proxy type : ')

    return proxy_type, filename, auth_required, proxy_api


def config_premium_proxy(category):
    auth_required = False
    proxy_api = False

    if category == 'r':
        print(bcolors.WARNING + '\n--> If you use the Proxy API link, script will scrape the proxy list on each thread start.' + bcolors.ENDC)
        print(bcolors.WARNING + '--> And will use one proxy randomly from that list to ensure session management.' + bcolors.ENDC)

        filename = ""
        while not filename:
            filename = str(input(
                bcolors.OKCYAN + '\nEnter your Rotating Proxy service Main Gateway or Proxy API link : ' + bcolors.ENDC))

        if 'http://' in filename or 'https://' in filename:
            proxy_api = True
            auth_required = input(bcolors.OKCYAN +
                                  '\nProxies need authentication? (default=No) [No/yes] : ' + bcolors.ENDC).lower()
            if auth_required == 'y' or auth_required == 'yes':
                auth_required = True
                proxy_type = 'http'
            else:
                auth_required = False

        else:
            if '@' in filename:
                auth_required = True
                proxy_type = 'http'
            elif filename.count(':') == 3:
                split = filename.split(':')
                filename = f'{split[2]}:{split[-1]}@{split[0]}:{split[1]}'
                auth_required = True
                proxy_type = 'http'

        if not auth_required:
            handle_proxy = str(input(
                bcolors.OKBLUE + "\nSelect proxy type [1 = HTTP , 2 = SOCKS4, 3 = SOCKS5] : " + bcolors.ENDC)).lower()
            while handle_proxy not in ['1', '2', '3']:
                handle_proxy = str(input(
                    '\nPlease input 1 for HTTP, 2 for SOCKS4 and 3 for SOCKS5 proxy type : ')).lower()

            proxy_type = PROXY_TYPES[handle_proxy]

    else:
        filename = ""
        while not filename:
            filename = str(input(
                bcolors.OKCYAN + '\nEnter your proxy File Name or Proxy API link : ' + bcolors.ENDC))
        auth_required = True
        proxy_type = 'http'
        if 'http://' in filename or 'https://' in filename:
            proxy_api = True

    return proxy_type, filename, auth_required, proxy_api


def config_proxy(config, category, refresh):
    category = input(bcolors.OKCYAN + "\nWhat's your proxy category? " +
                     "[F = Free, P = Premium, R = Rotating Proxy] : " + bcolors.ENDC).lower()
    try:
        if category not in ['f', 'p', 'r']:
            raise Exception('\nPlease input F for Free, P for Premium and R for Rotating proxy.')

        if category == 'f':
            proxy_type, filename, auth_required, proxy_api = config_free_proxy(
                category)

        elif category == 'p' or category == 'r':
            proxy_type, filename, auth_required, proxy_api = config_premium_proxy(
                category)

        if category != 'r' and filename:
            try:
                refresh = abs(float(refresh))
            except Exception:
                refresh = 0.0

        config["proxy"] = {
            "category": category,
            "proxy_type": proxy_type,
            "filename": filename,
            "authentication": auth_required,
            "proxy_api": proxy_api,
            "refresh": refresh
        }
    except: 
        config["proxy"] = {
            "category": "None",
            "proxy_type": "",
            "filename": "",
            "authentication": "",
            "proxy_api": "",
            "refresh": 0
        }
    return config


def config_gui(config):
    gui = str(input(
        bcolors.OKCYAN + '\nDo you want to run in headless(background) mode? (recommended=No) [No/yes] : ' + bcolors.ENDC)).lower()

    if gui == 'y' or gui == 'yes':
        background = True
    else:
        background = False

    config["background"] = background
    return config


def config_bandwidth(config):
    bandwidth = str(input(
        bcolors.OKBLUE + '\nReduce video quality to save Bandwidth? (recommended=No) [No/yes] : ' + bcolors.ENDC)).lower()

    if bandwidth == 'y' or bandwidth == 'yes':
        bandwidth = True
    else:
        bandwidth = False

    config["bandwidth"] = bandwidth
    return config


def config_playback(config):
    playback_speed = input(
        bcolors.OKBLUE + '\nChoose Playback speed [1 = Normal(1x), 2 = Slow(random .25x, .5x, .75x), 3 = Fast(random 1.25x, 1.5x, 1.75x)] (default = 1) : ' + bcolors.ENDC)
    try:
        playback_speed = int(playback_speed) if playback_speed in [
            '2', '3'] else 1
    except Exception:
        playback_speed = 1

    config["playback_speed"] = playback_speed
    return config


def config_threads(config):
    print(bcolors.WARNING +
          '\n--> Script will dynamically update thread amount when proxy reload happens.' + bcolors.ENDC)
    print(bcolors.WARNING +
          '--> If you wish to use the same amount of threads all the time, enter the same number in Maximum and Minimum threads.' + bcolors.ENDC)

    max_threads = input(
        bcolors.OKCYAN + '\nMaximum Threads [Amount of chrome driver you want to use] (recommended = 5): ' + bcolors.ENDC)
    try:
        max_threads = int(max_threads)
    except Exception:
        max_threads = 5

    min_threads = input(
        bcolors.OKCYAN + '\nMinimum Threads [Amount of chrome driver you want to use] (recommended = 2): ' + bcolors.ENDC)
    try:
        min_threads = int(min_threads)
    except Exception:
        min_threads = 2

    if min_threads >= max_threads:
        max_threads = min_threads

    config["max_threads"] = max_threads
    config["min_threads"] = min_threads
    return config

def create_config() -> None:
    config = {}

    config = config_api(config=config)

    config = config_database(config=config)

    config = config_views(config=config)

    config = config_min_max(config=config)

    config = config_proxy(config=config)

    config = config_gui(config=config)

    config = config_bandwidth(config=config)

    config = config_playback(config=config)

    config = config_threads(config=config)

    json_object = json.dumps(config, indent=4)

    with open(config_path, "w", encoding='utf-8-sig') as outfile:
        outfile.write(json_object)
