from utils.config import get_config
from youtubeviewer.proxies import scrape_api, load_proxy, gather_proxy

def get_config_by_params(*args):
    config = get_config()
    mapping_config = {
        "api" : config["http_api"]["enabled"],
        "host" : config["http_api"]["host"],
        "port" : config["http_api"]["port"],
        "database" : config["database"],
        "views" : config["views"],
        "minimum" : config["minimum"] / 100,
        "maximum" : config["maximum"] / 100,
        "category" : config["proxy"]["category"],
        "proxy_type" : config["proxy"]["proxy_type"],
        "filename" : config["proxy"]["filename"],
        "auth_required" : config["proxy"]["authentication"],
        "proxy_api" : config["proxy"]["proxy_api"],
        "refresh" : config["proxy"]["refresh"],
        "background" : config["background"],
        "bandwidth" : config["bandwidth"],
        "playback_speed" : config["playback_speed"],
        "max_threads" : config["max_threads"],
        "min_threads" : config["min_threads"],
    }
    return (mapping_config[param] for param in args)

def get_proxy_list():
    filename, category, max_threads, proxy_api = get_config_by_params("filename", "category", "max_threads", "proxy_api")
    if filename:
        if category == 'r':
            factor = max_threads if max_threads > 1000 else 1000
            proxy_list = [filename] * factor
        else:
            if proxy_api:
                proxy_list = scrape_api(filename)
            else:
                proxy_list = load_proxy(filename)

    else:
        proxy_list = gather_proxy()

    return proxy_list