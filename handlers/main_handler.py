import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gio, Gtk
import requests
import shutil
import io
import os
import threading
import re
import subprocess
import sys
import textwrap
import logging
from concurrent.futures import ThreadPoolExecutor, wait
from datetime import datetime
from glob import glob
from time import gmtime, sleep, strftime, time
from random import randint, choices

import psutil
from fake_headers import Headers, browsers
from faker import Faker
from requests.exceptions import RequestException
from tabulate import tabulate
from undetected_chromedriver.patcher import Patcher

from views.setting_view import SettingView
from views.url_view import UrlView
from views.proxy_view import ProxyView

from youtubeviewer import website
from youtubeviewer.config import create_config
from youtubeviewer.colors import *
from youtubeviewer.database import create_database
from youtubeviewer.download_driver import download_driver, copy_drivers
from youtubeviewer.load_files import get_hash, load_search, load_url
from youtubeviewer.proxies import scrape_api, check_proxy
from youtubeviewer.bypass import *
from youtubeviewer.features import *
from youtubeviewer.basics import (play_video, 
                                  search_video,
                                  play_music,
                                  get_driver)
from youtubeviewer.database import update_database
from youtube_viewer import detect_file_change

from utils.constants import (MAINVIEW_DIR, 
                             CONFIG_FILE_DIR, 
                             DATABASE_DIR, 
                             DATABASE_BACKUP_DIR,
                             HEADERS_1,
                             HEADERS_2,
                             VIEWPORTS,
                             REFERERS,
                             SCRIPT_VERSION,
                             PATCHED_DRIVERS_DIR)
from utils.helpers import get_proxy_list, get_config_by_params
import traceback

logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(message)s')

class MainHandler:
    
    def clean_exe_temp(self, folder):
        temp_name = None
        if hasattr(sys, '_MEIPASS'):
            temp_name = sys._MEIPASS.split('\\')[-1]
        else:
            if sys.version_info.minor < 7 or sys.version_info.minor > 11:
                print(
                    f'Your current python version is not compatible : {sys.version}')
                print(f'Install Python version between 3.7.x to 3.11.x to run this script')
                input("")
                sys.exit()

        for f in glob(os.path.join('temp', folder, '*')):
            if temp_name not in f:
                shutil.rmtree(f, ignore_errors=True)
    
    def check_update(self):
        api_url = 'https://api.github.com/repos/MShawon/YouTube-Viewer/releases/latest'
        try:
            response = requests.get(api_url, timeout=30)

            RELEASE_VERSION = response.json()['tag_name']

            if RELEASE_VERSION > SCRIPT_VERSION:
                print(bcolors.OKCYAN + '#'*100 + bcolors.ENDC)
                print(bcolors.OKCYAN + 'Update Available!!! ' +
                    f'YouTube Viewer version {SCRIPT_VERSION} needs to update to {RELEASE_VERSION} version.' + bcolors.ENDC)

                try:
                    notes = response.json()['body'].split(
                        'SHA256')[0].split('\r\n')
                    for note in notes:
                        if note:
                            print(bcolors.HEADER + note + bcolors.ENDC)
                except Exception:
                    pass
                print(bcolors.OKCYAN + '#'*100 + '\n' + bcolors.ENDC)
        except Exception:
            pass


    def update_chrome_version(self):
        link = 'https://gist.githubusercontent.com/MShawon/29e185038f22e6ac5eac822a1e422e9d/raw/versions.txt'

        output = requests.get(link, timeout=60).text
        chrome_versions = output.split('\n')

        browsers.chrome_ver = chrome_versions

    def __init__(self):
        self.futures = ''
        self.osname = ''
        self.exe_name = ''
        self.total_proxies = 0
        self.queries = []
        self.urls = []
        self.driver_dict = {}
        self.checked = {}
        self.proxy_list = []
        self.cancel_all = False
        self.temp_folders = []
        self.duration_dict = {}
        self.summary = {}
        self.checked = {}
        self.threads = 0
        self.view = []
        self.video_statistics = {}
        self.bad_proxies = []
        self.suggested = []
        self.used_proxies = []
        self.proxies_from_api = []
        self.console = []
        self.viewports = VIEWPORTS
        self.referers = REFERERS
        self.constructor = None
        self.width = 0

        self.cwd = os.getcwd()
        self.fake = Faker()
        self.date_fmt = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        self.cpu_usage = str(psutil.cpu_percent(1))

        self.clean_exe_temp(folder='youtube_viewer')
        self.update_chrome_version()
        self.check_update()
        self.osname, self.exe_name = download_driver(patched_drivers=PATCHED_DRIVERS_DIR)
        create_database(database=DATABASE_DIR, database_backup=DATABASE_BACKUP_DIR)

        website.console = self.console
        website.database = DATABASE_DIR
        if self.osname == 'win':
            import wmi
            self.constructor = wmi.WMI()

        self.urls, self.message = load_url()
        self.queries = load_search()
        
        hash_urls = get_hash("urls.txt")
        hash_queries = get_hash("search.txt")
        hash_config = get_hash(CONFIG_FILE_DIR)

        builder = Gtk.Builder()
        builder.add_from_file(MAINVIEW_DIR)
        self.display_text_view = builder.get_object("result-text")
        self.display_text_view.set_buffer(Gtk.TextBuffer())        
    
    def monkey_patch_exe(self):
        linect = 0
        replacement = self.gen_random_cdc()
        replacement = f"  var key = '${replacement.decode()}_';\n".encode()
        with io.open(self.executable_path, "r+b") as fh:
            for line in iter(lambda: fh.readline(), b""):
                if b"var key = " in line:
                    fh.seek(-len(line), 1)
                    fh.write(replacement)
                    linect += 1
            return linect
    
    def timestamp(self):
        self.date_fmt = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        return bcolors.OKGREEN + f'[{self.date_fmt}] | ' + bcolors.OKCYAN + f'{self.cpu_usage} | '

    def create_html(self, text_dict):
        if len(self.console) > 250:
            self.console.pop()

        date = f'<span style="color:#23d18b"> [{self.date_fmt}] | </span>'
        cpu = f'<span style="color:#29b2d3"> {self.cpu_usage} | </span>'
        str_fmt = ''.join(
            [f'<span style="color:{key}"> {value} </span>' for key, value in text_dict.items()])
        html = date + cpu + str_fmt

        self.console.insert(0, html)
   
    def set_text(self, text_view, text):
        buffer = text_view.get_buffer()
        print(buffer)
        print(text)        
        buffer.set_text(text)

    def direct_or_search(self, position):
        keyword = None
        video_title = None
        if position % 2:
            try:
                method = 1
                url = choice(self.urls)
                if 'music.youtube.com' in url:
                    youtube = 'Music'
                else:
                    youtube = 'Video'
            except IndexError:
                raise Exception("Your urls.txt is empty!")

        else:
            try:
                method = 2
                query = choice(self.queries)
                keyword = query[0]
                video_title = query[1]
                url = "https://www.youtube.com"
                youtube = 'Video'
            except IndexError:
                try:
                    youtube = 'Music'
                    url = choice(self.urls)
                    if 'music.youtube.com' not in url:
                        raise Exception
                except Exception:
                    raise Exception("Your search.txt is empty!")

        return url, method, youtube, keyword, video_title


    def features(self, driver):
        bandwidth, playback_speed = get_config_by_params(
            "bandwidth", "playback_speed"
        )
        if bandwidth:
            save_bandwidth(driver)
        bypass_popup(driver)
        bypass_other_popup(driver)
        play_video(driver)
        change_playback_speed(driver, playback_speed)


    def update_view_count(self, position):
        max_threads, min_threads = get_config_by_params("max_threads", "min_threads")
        self.view.append(position)
        view_count = len(self.view)
        print(self.timestamp() + bcolors.OKCYAN +
            f'Worker {position} | View added : {view_count}' + bcolors.ENDC)

        self.create_html({"#29b2d3": f'Worker {position} | View added : {view_count}'})

        if DATABASE_DIR:
            try:
                update_database(
                    database=DATABASE_DIR, threads=max_threads)
            except Exception:
                pass


    def set_referer(self, position, url, method, driver):
        referer = choice(self.referers)
        if referer:
            if method == 2 and 't.co/' in referer:
                driver.get(url)
            else:
                if 'search.yahoo.com' in referer:
                    driver.get('https://duckduckgo.com/')
                    driver.execute_script(
                        "window.history.pushState('page2', 'Title', arguments[0]);", referer)
                else:
                    driver.get(referer)

                driver.execute_script(
                    "window.location.href = '{}';".format(url))

            print(self.timestamp() + bcolors.OKBLUE +
                f"Worker {position} | Referer used : {referer}" + bcolors.ENDC)

            self.self.create_html(
                {"#3b8eea": f"Worker {position} | Referer used : {referer}"})

        else:
            driver.get(url)

    def youtube_normal(self, method, keyword, video_title, driver, output):
        if method == 2:
            msg = search_video(driver, keyword, video_title)
            if msg == 'failed':
                raise Exception(
                    f"Can't find this [{video_title}] video with this keyword [{keyword}]")

        skip_initial_ad(driver, output, self.duration_dict)

        try:
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
                (By.ID, 'movie_player')))
        except WebDriverException:
            raise Exception(
                "Slow internet speed or Stuck at reCAPTCHA! Can't load YouTube...")

        self.features(driver)

        try:
            view_stat = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#count span'))).text
            if not view_stat:
                raise WebDriverException
        except WebDriverException:
            view_stat = driver.find_element(
                By.XPATH, '//*[@id="info"]/span[1]').text

        return view_stat


    def youtube_music(driver):
        if 'coming-soon' in driver.title or 'not available' in driver.title:
            raise Exception(
                "YouTube Music is not available in your area!")
        try:
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="player-page"]')))
        except WebDriverException:
            raise Exception(
                "Slow internet speed or Stuck at reCAPTCHA! Can't load YouTube...")

        bypass_popup(driver)

        play_music(driver)

        output = driver.find_element(
            By.XPATH, '//ytmusic-player-bar//yt-formatted-string').text
        view_stat = 'music'

        return view_stat, output


    def spoof_timezone_geolocation(self, proxy_type, proxy, driver):
        try:
            proxy_dict = {
                "http": f"{proxy_type}://{proxy}",
                        "https": f"{proxy_type}://{proxy}",
            }
            resp = requests.get(
                "http://ip-api.com/json", proxies=proxy_dict, timeout=30)

            if resp.status_code == 200:
                location = resp.json()
                tz_params = {'timezoneId': location['timezone']}
                latlng_params = {
                    "latitude": location['lat'],
                    "longitude": location['lon'],
                    "accuracy": randint(20, 100)
                }
                info = f"ip-api.com | Lat : {location['lat']} | Lon : {location['lon']} | TZ: {location['timezone']}"
            else:
                raise RequestException

        except RequestException:
            location = self.fake.location_on_land()
            tz_params = {'timezoneId': location[-1]}
            latlng_params = {
                "latitude": location[0],
                "longitude": location[1],
                "accuracy": randint(20, 100)
            }
            info = f"Random | Lat : {location[0]} | Lon : {location[1]} | TZ: {location[-1]}"

        try:
            driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)

            driver.execute_cdp_cmd(
                "Emulation.setGeolocationOverride", latlng_params)

        except WebDriverException:
            pass

        return info

    def control_player(self, driver, output, position, proxy, youtube, collect_id=True):
        minimum, maximum = get_config_by_params("minimum_threads", "maximum_threads")
        current_url = driver.current_url

        video_len = self.duration_dict.get(output, 0)
        for _ in range(90):
            if video_len != 0:
                self.duration_dict[output] = video_len
                break

            video_len = driver.execute_script(
                "return document.getElementById('movie_player').getDuration()")
            sleep(1)

        if video_len == 0:
            raise Exception('Video player is not loading...')

        actual_duration = strftime(
            "%Hh:%Mm:%Ss", gmtime(video_len)).lstrip("0h:0m:")
        video_len = video_len*uniform(minimum, maximum)
        duration = strftime("%Hh:%Mm:%Ss", gmtime(video_len)).lstrip("0h:0m:")

        if len(output) == 11:
            output = driver.title[:-10]

        self.summary[position] = [position, output, f'{duration} / {actual_duration}']
        website.summary_table = tabulate(
            self.summary.values(), headers=HEADERS_1, numalign='center', stralign='center', tablefmt="html")

        GLib.idle_add(self.set_text, self.display_text_view, (self.timestamp() + bcolors.OKBLUE + f"Worker {position} | " + bcolors.OKGREEN +
            f"{proxy} --> {youtube} Found : {output} | Watch Duration : {duration} " + bcolors.ENDC),)

        self.self.create_html({"#3b8eea": f"Worker {position} | ",
                    "#23d18b": f"{proxy.split('@')[-1]} --> {youtube} Found : {output} | Watch Duration : {duration} "})

        if youtube == 'Video' and collect_id:
            try:
                video_id = re.search(
                    r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", current_url).group(1)
                if video_id not in self.suggested and output in driver.title:
                    self.suggested.append(video_id)
            except Exception:
                pass

        try:
            current_channel = driver.find_element(
                By.CSS_SELECTOR, '#upload-info a').text
        except WebDriverException:
            current_channel = 'Unknown'

        error = 0
        loop = int(video_len/4)
        for _ in range(loop):
            sleep(5)
            current_time = driver.execute_script(
                "return document.getElementById('movie_player').getCurrentTime()")

            if youtube == 'Video':
                play_video(driver)
                random_command(driver)
            elif youtube == 'Music':
                play_music(driver)

            current_state = driver.execute_script(
                "return document.getElementById('movie_player').getPlayerState()")
            if current_state in [-1, 3]:
                error += 1
            else:
                error = 0

            if error == 10:
                error_msg = f'Taking too long to play the video | Reason : buffering'
                if current_state == -1:
                    error_msg = f"Failed to play the video | Possible Reason : {proxy.split('@')[-1]} not working anymore"
                raise Exception(error_msg)

            elif current_time > video_len or driver.current_url != current_url:
                break

        self.summary.pop(position, None)
        website.summary_table = tabulate(
            self.summary.values(), headers=HEADERS_1, numalign='center', stralign='center', tablefmt="html")

        output = textwrap.fill(text=output, width=75, break_on_hyphens=False)
        self.video_statistics[output] = self.video_statistics.get(output, 0) + 1
        website.html_table = tabulate(self.video_statistics.items(), headers=HEADERS_2,
                                    showindex=True, numalign='center', stralign='center', tablefmt="html")

        return current_url, current_channel
        
    def youtube_live(self, proxy, position, driver, output):
        error = 0
        while True:
            try:
                view_stat = driver.find_element(
                    By.CSS_SELECTOR, '#count span').text
                if not view_stat:
                    raise WebDriverException
            except WebDriverException:
                view_stat = driver.find_element(
                    By.XPATH, '//*[@id="info"]/span[1]').text
            if 'watching' in view_stat:
                self.set_text(self.display_text_view, self.timestamp() + f"Worker {position} | " +
                    f"{proxy} | {output} | " + f"{view_stat} ")

                self.create_html({"#3b8eea": f"Worker {position} | ",
                            "#23d18b": f"{proxy.split('@')[-1]} | {output} | ", "#29b2d3": f"{view_stat} "})
            else:
                error += 1

            play_video(driver)

            random_command(driver)

            if error == 5:
                break
            sleep(60)

        self.update_view_count(position)


    def music_and_video(self, proxy, position, youtube, driver, output, view_stat):
        rand_choice = 1
        if len(self.suggested) > 1 and view_stat != 'music':
            rand_choice = randint(1, 3)

        for i in range(rand_choice):
            if i == 0:
                current_url, current_channel = self.control_player(
                    driver, output, position, proxy, youtube, collect_id=True)

                self.update_view_count(position)

            else:
                print(self.timestamp() + bcolors.OKBLUE +
                    f"Worker {position} | Suggested video loop : {i}" + bcolors.ENDC)

                self.create_html(
                    {"#3b8eea": f"Worker {position} | Suggested video loop : {i}"})

                try:
                    output = play_next_video(driver, self.suggested)
                except WebDriverException as e:
                    raise Exception(
                        f"Error suggested | {type(e).__name__} | {e.args[0] if e.args else ''}")

                print(self.timestamp() + bcolors.OKBLUE +
                    f"Worker {position} | Found next suggested video : [{output}]" + bcolors.ENDC)

                self.create_html(
                    {"#3b8eea": f"Worker {position} | Found next suggested video : [{output}]"})

                skip_initial_ad(driver, output, self.duration_dict)

                self.features(driver)

                current_url, current_channel = self.control_player(
                    driver, output, position, proxy, youtube, collect_id=False)

                self.update_view_count(position)

        return current_url, current_channel


    def channel_or_endscreen(self, proxy, position, youtube, driver, view_stat, current_url, current_channel):
        option = 1
        if view_stat != 'music' and driver.current_url == current_url:
            option = choices([1, 2, 3], cum_weights=(0.5, 0.75, 1.00), k=1)[0]

            if option == 2:
                try:
                    output, log, option = play_from_channel(
                        driver, current_channel)
                except WebDriverException as e:
                    raise Exception(
                        f"Error channel | {type(e).__name__} | {e.args[0] if e.args else ''}")

                self.set_text(self.display_text_view, self.timestamp() +
                    f"Worker {position} | {log}")

                self.create_html({"#3b8eea": f"Worker {position} | {log}"})

            elif option == 3:
                try:
                    output = play_end_screen_video(driver)
                except WebDriverException as e:
                    raise Exception(
                        f"Error end screen | {type(e).__name__} | {e.args[0] if e.args else ''}")

                print(self.timestamp() +
                    f"Worker {position} | Video played from end screen : [{output}]")

                self.create_html(
                    {"#3b8eea": f"Worker {position} | Video played from end screen : [{output}]"})

            if option in [2, 3]:
                skip_initial_ad(driver, output, self.duration_dict)

                self.features(driver)

                current_url, current_channel = self.control_player(
                    driver, output, position, proxy, youtube, collect_id=False)

            if option in [2, 3, 4]:
                self.update_view_count(position)


    def windows_kill_drivers(self):
        for process in self.constructor.Win32_Process(["CommandLine", "ProcessId"]):
            try:
                if 'UserAgentClientHint' in process.CommandLine:
                    print(f'Killing PID : {process.ProcessId}', end="\r")
                    subprocess.Popen(['taskkill', '/F', '/PID', f'{process.ProcessId}'],
                                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
            except Exception:
                pass
        print('\n')


    def quit_driver(self, driver, data_dir):
        if driver and driver in self.driver_dict:
            driver.quit()
            if data_dir in self.temp_folders:
                self.temp_folders.remove(data_dir)

        proxy_folder = self.driver_dict.pop(driver, None)
        if proxy_folder:
            shutil.rmtree(proxy_folder, ignore_errors=True)

        status = 400
        return status


    def main_viewer(self, proxy_type, proxy, position):
        driver = None
        data_dir = None
        category, proxy_api, background, auth_required = get_config_by_params(
            "category", "proxy_api", "background", "auth_required"
        )

        if self.cancel_all:
            raise KeyboardInterrupt

        try:
            detect_file_change()

            self.checked[position] = None

            header = Headers(
                browser="chrome",
                os=self.osname,
                headers=False
            ).generate()
            agent = header['User-Agent']

            url, method, youtube, keyword, video_title = self.direct_or_search(position)

            if category == 'r' and proxy_api:
                for _ in range(20):
                    proxy = choice(self.proxies_from_api)
                    if proxy not in self.used_proxies:
                        break
                self.used_proxies.append(proxy)

            status = check_proxy(category, agent, proxy, proxy_type)

            if status != 200:
                raise RequestException(status)

            try:
                print(self.timestamp() + bcolors.OKBLUE + f"Worker {position} | " + bcolors.OKGREEN +
                    f"{proxy} | {proxy_type.upper()} | Good Proxy | Opening a new driver..." + bcolors.ENDC)

                self.create_html({"#3b8eea": f"Worker {position} | ",
                            "#23d18b": f"{proxy.split('@')[-1]} | {proxy_type.upper()} | Good Proxy | Opening a new driver..."})

                while proxy in self.bad_proxies:
                    self.bad_proxies.remove(proxy)
                    sleep(1)

                patched_driver = os.path.join(
                    PATCHED_DRIVERS_DIR, f'chromedriver_{position%self.threads}{self.exe_name}')

                try:
                    Patcher.patch_exe = self.monkey_patch_exe
                    Patcher(executable_path=patched_driver).patch_exe()
                except Exception:
                    pass

                proxy_folder = os.path.join(
                    self.cwd, 'extension', f'proxy_auth_{position}')

                factor = int(self.threads/(0.1*self.threads + 1))
                sleep_time = int((str(position)[-1])) * factor
                sleep(sleep_time)
                if self.cancel_all:
                    raise KeyboardInterrupt

                driver = get_driver(background, self.viewports, agent, auth_required,
                                    patched_driver, proxy, proxy_type, proxy_folder)

                self.driver_dict[driver] = proxy_folder

                data_dir = driver.capabilities['chrome']['userDataDir']
                self.temp_folders.append(data_dir)

                sleep(2)

                info = self.spoof_timezone_geolocation(proxy_type, proxy, driver)

                isdetected = driver.execute_script('return navigator.webdriver')

                print(self.timestamp() + bcolors.OKBLUE + f"Worker {position} | " + bcolors.OKGREEN +
                    f"{proxy} | {proxy_type.upper()} | " + bcolors.OKCYAN + f"{info} | Detected? : {isdetected}" + bcolors.ENDC)

                self.create_html({"#3b8eea": f"Worker {position} | ",
                            "#23d18b": f"{proxy.split('@')[-1]} | {proxy_type.upper()} | ", "#29b2d3": f"{info} | Detected? : {isdetected}"})

                if self.width == 0:
                    self.width = driver.execute_script('return screen.width')
                    height = driver.execute_script('return screen.height')
                    print(f'Display resolution : {self.width}x{height}')
                    self.viewports = [i for i in self.viewports if int(i[:4]) <= self.width]

                try:
                    self.set_referer(position, url, method, driver)
                except Exception as e:
                    print(e)
                    traceback.print_exc()

                if 'consent' in driver.current_url:
                    print(self.timestamp() + bcolors.OKBLUE +
                        f"Worker {position} | Bypassing consent..." + bcolors.ENDC)

                    self.create_html(
                        {"#3b8eea": f"Worker {position} | Bypassing consent..."})

                    bypass_consent(driver)

                if video_title:
                    output = video_title
                else:
                    output = driver.title[:-10]

                if youtube == 'Video':
                    view_stat = self.youtube_normal(
                        method, keyword, video_title, driver, output)
                else:
                    view_stat, output = self.youtube_music(driver)

                if 'watching' in view_stat:
                    self.youtube_live(proxy, position, driver, output)

                else:
                    current_url, current_channel = self.music_and_video(
                        proxy, position, youtube, driver, output, view_stat)

                self.channel_or_endscreen(proxy, position, youtube,
                                    driver, view_stat, current_url, current_channel)

                if randint(1, 2) == 1:
                    try:
                        driver.find_element(By.ID, 'movie_player').send_keys('k')
                    except WebDriverException:
                        pass

                status = self.quit_driver(driver=driver, data_dir=data_dir)

            except Exception as e:
                status = self.quit_driver(driver=driver, data_dir=data_dir)

                print(self.timestamp() + bcolors.FAIL +
                    f"Worker {position} | Line : {e.__traceback__.tb_lineno} | {type(e).__name__} | {e.args[0] if e.args else ''}" + bcolors.ENDC)

                self.create_html(
                    {"#f14c4c": f"Worker {position} | Line : {e.__traceback__.tb_lineno} | {type(e).__name__} | {e.args[0] if e.args else ''}"})

        except RequestException:
            print(self.timestamp() + bcolors.OKBLUE + f"Worker {position} | " +
                bcolors.FAIL + f"{proxy} | {proxy_type.upper()} | Bad proxy " + bcolors.ENDC)

            self.create_html({"#3b8eea": f"Worker {position} | ",
                        "#f14c4c": f"{proxy.split('@')[-1]} | {proxy_type.upper()} | Bad proxy "})

            self.checked[position] = proxy_type
            self.bad_proxies.append(proxy)

        except Exception as e:
            print(self.timestamp() + bcolors.FAIL +
                f"Worker {position} | Line : {e.__traceback__.tb_lineno} | {type(e).__name__} | {e.args[0] if e.args else ''}" + bcolors.ENDC)

            self.create_html(
                {"#f14c4c": f"Worker {position} | Line : {e.__traceback__.tb_lineno} | {type(e).__name__} | {e.args[0] if e.args else ''}"})

    def stop_server(self, immediate=False):
        api, host, port = get_config_by_params("api", "host", "port")
        if not immediate:
            self.set_text(self.display_text_view,
                          'Allowing a maximum of 15 minutes to finish all the running drivers...')
            for _ in range(180):
                sleep(5)
                if 'state=running' not in str(self.futures[1:-1]):
                    break

        if api:
            for _ in range(10):
                response = requests.post(f'http://127.0.0.1:{port}/shutdown')
                if response.status_code == 200:
                    self.set_text(self.display_text_view, 'Server shut down successfully!')
                    break
                else:
                    self.set_text(self.display_text_view,
                                  f'Server shut down error : {response.status_code}')
                    sleep(3)


    def clean_exit(self):
        self.set_text(self.display_text_view,
                      self.timestamp() + 'Cleaning up processes...')
        self.create_html({"#f3f342": "Cleaning up processes..."})

        if self.osname == 'win':
            self.driver_dict.clear()
            # self.windows_kill_drivers()
        else:
            for driver in list(self.driver_dict):
                self.quit_driver(driver=driver, data_dir=None)

        for folder in self.temp_folders:
            shutil.rmtree(folder, ignore_errors=True)

    def cancel_pending_task(self, not_done):

        self.cancel_all = True
        for future in not_done:
            _ = future.cancel()

        self.clean_exit()

        self.stop_server(immediate=True)
        _ = wait(not_done, timeout=None)

        self.clean_exit()

    def view_video(self, position, event):
        try:
            proxy_type, host, port, api = get_config_by_params(
                "proxy_type", "host", "port", "api"
            )        
            if position == 0:
                if api:
                    website.start_server(host=host, port=port)

            elif position == self.total_proxies - 1:
                self.stop_server(immediate=False)
                self.clean_exit()

            else:
                sleep(2)
                proxy = self.proxy_list[position]

                if proxy_type:
                    self.main_viewer(proxy_type, proxy, position)
                elif '|' in proxy:
                    splitted = proxy.split('|')
                    self.main_viewer(splitted[-1], splitted[0], position)
                else:
                    self.main_viewer('http', proxy, position)
                    if self.checked[position] == 'http':
                        self.main_viewer('socks4', proxy, position)
                    if self.checked[position] == 'socks4':
                        self.main_viewer('socks5', proxy, position)
        except:
            traceback.print_exc()
        event.set()

    def main_thread(self):
        views = 100
        event = threading.Event()
        category, proxy_api, filename, min_threads, max_threads, refresh, api =\
            get_config_by_params("category", "proxy_api", "filename", 
                                 "min_threads", "max_threads", "refresh", 
                                 "api")
        start_time = time()
        hash_config = get_hash(CONFIG_FILE_DIR)

        self.proxy_list = get_proxy_list()
        self.set_text(self.display_text_view, "Hello")
        if category != 'r':
            self.set_text(self.display_text_view, 
                          f'Total proxies : {len(self.proxy_list)}')

        self.proxy_list = [x for x in self.proxy_list if x not in self.bad_proxies]
        if len(self.proxy_list) == 0:
            self.bad_proxies.clear()
            self.proxy_list = get_proxy_list()
        if self.proxy_list[0] != 'dummy':
            self.proxy_list.insert(0, 'dummy')
        if self.proxy_list[-1] != 'dummy':
            self.proxy_list.append('dummy')
        self.total_proxies = len(self.proxy_list)

        if category == 'r' and proxy_api:
            self.proxies_from_api = scrape_api(link=filename)

        self.threads = randint(min_threads, max_threads)
        if api:
            self.threads += 1

        loop = 0
        pool_number = list(range(self.total_proxies))
        print("we are here")

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            try:
                futures = [executor.submit(self.view_video, position, event)
                    for position in pool_number]
            except:
                traceback.print_exc()
            done, not_done = wait(futures, timeout=0)
            try:
                while not_done:
                    freshly_done, not_done = wait(not_done, timeout=1)
                    done |= freshly_done

                    loop += 1
                    for _ in range(70):
                        cpu = str(psutil.cpu_percent(0.2))
                        self.cpu_usage = cpu + '%' + ' ' * \
                            (5-len(cpu)) if cpu != '0.0' else self.cpu_usage

                    if loop % 40 == 0:
                        print(tabulate(self.video_statistics.items(),
                            headers=HEADERS_2, showindex=True, tablefmt="pretty"))

                    if category == 'r' and proxy_api:
                        self.proxies_from_api = scrape_api(link=filename)

                    if len(self.view) >= views:
                        GLib.idle_add(self.set_text, self.display_text_view, self.timestamp() + f'Amount of views added : {views} | Stopping program...')
                        self.create_html(
                            {"#f3f342": f'Amount of views added : {views} | Stopping program...'})

                        self.cancel_pending_task(not_done=not_done)
                        break

                    elif hash_config != get_hash(CONFIG_FILE_DIR):
                        hash_config = get_hash(CONFIG_FILE_DIR)
                        GLib.idle_add(self.set_text, self.display_text_view, self.timestamp() + 
                            'Modified config.json will be in effect soon...')
                        self.create_html(
                            {"#f3f342": 'Modified config.json will be in effect soon...'})

                        self.cancel_pending_task(not_done=not_done)
                        break

                    elif refresh != 0 and category != 'r':

                        if (time() - start_time) > refresh*60:
                            start_time = time()

                            proxy_list_new = get_proxy_list()
                            proxy_list_new = [
                                x for x in proxy_list_new if x not in self.bad_proxies]

                            proxy_list_old = [
                                x for x in self.proxy_list[1:-1] if x not in self.bad_proxies]

                            if sorted(proxy_list_new) != sorted(proxy_list_old):
                                print(self.timestamp() + bcolors.WARNING +
                                    f'Refresh {refresh} minute triggered. Proxies will be reloaded soon...' + bcolors.ENDC)
                                self.create_html(
                                    {"#f3f342": f'Refresh {refresh} minute triggered. Proxies will be reloaded soon...'})

                                self.cancel_pending_task(not_done=not_done)
                                break

            except KeyboardInterrupt:
                print(self.timestamp() + bcolors.WARNING +
                    'Hold on!!! Allow me a moment to close all the running drivers.' + bcolors.ENDC)
                self.create_html(
                    {"#f3f342": 'Hold on!!! Allow me a moment to close all the running drivers.'})

                self.cancel_pending_task(not_done=not_done)
                raise KeyboardInterrupt
        pass
    
    def on_add_url_pressed(self, *args):
        url_dialog = UrlView()
        url_dialog.present()

    def add_proxy_pressed(self, *args):
        proxy_dialog = ProxyView()
        proxy_dialog.present()

    def on_settings_pressed(self, *args):
        setting_dialog = SettingView()
        response = setting_dialog.run()
        if response == Gtk.ResponseType.OK:
            print("OK button clicked")
            print(setting_dialog.__dict__)
        else:
            print("Dialog closed")

        setting_dialog.destroy()
    
    def do_background(self, views, max_threads):
        thread = threading.current_thread()
        logging.debug(f'main thread {thread.ident} starts ')
        if len(self.view) < views:
            copy_drivers(cwd=self.cwd, patched_drivers=PATCHED_DRIVERS_DIR,
                         exe=self.exe_name, total=max_threads)

            self.main_thread()

    def on_run_clicked(self, window):
        logging.debug('Button clicked in main thread')
        
        GLib.idle_add(self.set_text, self.display_text_view, self.message)
        print(self.urls)
        self.set_text(self.display_text_view, "Hello")
        buffer = self.display_text_view.get_buffer()         
        buffer.set_text("Hello \n")
        builder = Gtk.Builder()
        builder.add_from_file(MAINVIEW_DIR)
        window = builder.get_object("result-text")
        window.show_all()
        buffer = Gtk.TextBuffer()
        buffer.insert_at_cursor("Good bye \n")
        self.display_text_view.set_buffer(buffer)
        print(self.display_text_view)
        window = builder.get_object("result-text")
        print(window.get_visible())
        window.show_all()        
        buffer.insert(buffer.get_end_iter(), "Button clicked\n")
        # with ThreadPoolExecutor(max_workers=2) as exec:
        #     views, max_threads = get_config_by_params("views", "max_threads")
        #     future = exec.submit(self.do_background, views, max_threads)
        