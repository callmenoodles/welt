import os
import json
import time
import glob
import atexit
import tomllib
import threading
import subprocess
from urllib.parse import urlparse

from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxWebDriver
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver
from codecarbon import OfflineEmissionsTracker
from selenium import webdriver
from datetime import datetime
import pandas as pd
import numpy as np

driver: FirefoxWebDriver | ChromeWebDriver | None = None
tracker: OfflineEmissionsTracker | None = None
event = threading.Event()


def get_timestamp():
    return datetime.now().strftime('%Y-%m-%dT%H:%M:%S')


def get_domain(url):
    return str(urlparse(url).netloc)


run_id = get_timestamp()


def output_to_csv(row):
    path = os.path.join('out', f'{run_id}.csv')
    header = ('url,tool,timestamp,duration,energy,cpu_power,cpu_energy,gpu_power,gpu_energy,ram_power,'
              'ram_energy,emissions,emissions_rate')

    if os.path.isfile(path):
        row.to_csv(path, mode='a', header=False, index=False)
    else:
        row.to_csv(path, header=header, index=False)


def load_config():
    with open('config.toml', 'rb') as f:
        return tomllib.load(f)


def run_scaphandre(url, duration):
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    domain = url
    config = load_config()

    if "os" not in url.lower():
        domain = get_domain(url)

    out_path = os.path.join('out', 'tmp', f'scaphandre-{domain}.json')

    subprocess.run([config.get('scaphandre_path'), 'json', '-t', str(duration), '-s', '1', '-f', out_path])

    with open(out_path, 'r') as f:
        raw = json.load(f)
        consumption = []

        for reading in raw:
            consumption.append(reading['host']['consumption'])

        mean_consumption = np.mean(consumption)

        row = {
            'url': url,
            'tool': 'scaphandre',
            'timestamp': timestamp,
            'duration': float(duration),
            'energy': mean_consumption / 10 ** 6,
            'cpu_power': '',
            'cpu_energy': '',
            'gpu_power': '',
            'gpu_energy': '',
            'ram_power': '',
            'ram_energy': '',
            'emissions': '',
            'emissions_rate': '',
        }

        output_to_csv(pd.DataFrame([row]))


def output_codecarbon():
    tmp_path = glob.glob(os.path.join('out', 'tmp', 'emissions*.csv'))[0]
    tmp_rows = pd.read_csv(tmp_path)

    for i, tmp_row in tmp_rows.iterrows():
        row = {
            'url': tmp_row['task_name'],
            'tool': 'codecarbon',
            'timestamp': tmp_row['timestamp'],
            'duration': tmp_row['duration'],
            'energy': tmp_row['energy_consumed'],
            'cpu_power': tmp_row['cpu_power'],
            'cpu_energy': tmp_row['cpu_energy'],
            'gpu_power': tmp_row['gpu_power'],
            'gpu_energy': tmp_row['gpu_power'],
            'ram_power': tmp_row['ram_power'],
            'ram_energy': tmp_row['ram_energy'],
            'emissions': tmp_row['emissions'],
            'emissions_rate': tmp_row['emissions_rate'],
        }

        output_to_csv(pd.DataFrame([row]))


def run_codecarbon(url, duration):
    global tracker

    def end_codecarbon(url):
        tracker.stop_task(url)
        event.set()

    event.clear()
    tracker.start_task(url)
    threading.Timer(duration, end_codecarbon, args=[url]).start()
    event.wait()


def measure(url, duration, delay, tool):
    print(f"\nLoading {url}...")

    try:
        if url != 'os':
            driver.get(url)

        time.sleep(delay)

        match tool:
            case "scaphandre":
                run_scaphandre(url, duration)
            case "codecarbon":
                run_codecarbon(url, duration)

    except Exception as e:
        print(f"Failed to load {url}:\n{str(e)}")


def clean_tmp():
    csvs = glob.glob(os.path.join('out', 'tmp', '*.csv'))
    jsons = glob.glob(os.path.join('out', 'tmp', '*.json'))

    for file in csvs + jsons:
        os.remove(file)


def main():
    global driver, tracker, run_id
    config = load_config()

    tool = config.get('tool')
    browser = config.get('browser')
    duration = config.get('duration')
    delay = config.get('delay')
    repeat = config.get('repeat')
    dataset = config.get('dataset')

    ff_options = webdriver.FirefoxOptions()
    ff_options.add_argument('--private')
    ff_options.set_preference('browser.cache.disk.enable', False)
    ff_options.set_preference('browser.cache.memory.enable', False)
    ff_options.set_preference('browser.cache.offline.enable', False)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--disk-cache-size=0')

    for i in range(repeat):
        clean_tmp()
        run_id = get_timestamp()

        if tool == 'codecarbon':
            tracker = OfflineEmissionsTracker(measure_power_secs=duration)

        # Measure baseline
        measure("os", duration, delay, tool)

        if browser == 'firefox':
            driver = webdriver.Firefox(options=ff_options)
        elif browser == 'chrome':
            driver = webdriver.Chrome(options=chrome_options)

        measure("about:blank", duration, delay, tool)

        # Measure URLs
        with open(os.path.join('data', f'{dataset}.json'), 'r') as f:
            urls = json.load(f)

            for url in urls:
                measure(url, duration, delay, tool)

            if tool == 'codecarbon':
                tracker.stop()
                output_codecarbon()

        driver.quit()


if __name__ == '__main__':
    main()
