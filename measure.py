import json
from urllib.parse import urlparse
import numpy as np
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxWebDriver
from codecarbon import OfflineEmissionsTracker
from selenium import webdriver
from datetime import datetime
from typing import Literal
import pandas as pd
import subprocess
import threading
import os.path
import atexit
import time
import os

_TOOLS = Literal['scaphandre', 'codecarbon', 'powerjoular']
driver: FirefoxWebDriver | None = None
tracker = OfflineEmissionsTracker()
event = threading.Event()


def get_timestamp():
    return datetime.now().strftime('%Y-%m-%dT%H:%M:%S')


run_id = get_timestamp()


def get_domain(url):
    return str(urlparse(url).netloc)


def output_to_csv(row):
    path = f'out/{run_id}.csv'
    header = ('url,tool,timestamp,duration,energy,cpu_power,cpu_energy,gpu_power,gpu_energy,ram_power,'
              'ram_energy,emissions,emissions_rate')

    if os.path.isfile(path):
        row.to_csv(path, mode='a', header=False, index=False)
    else:
        row.to_csv(path, header=header, index=False)


def run_scaphandre(url, duration):
    timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    domain = get_domain(url)

    subprocess.run(["/usr/local/src/scaphandre/target/release/scaphandre", 'json', '-t', str(duration),
                    '-s', '1', '-f', f'out/tmp/scaphandre-{domain}.json'])

    with open(f'out/tmp/scaphandre-{domain}.json', 'r') as f:
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
        }

        output_to_csv(pd.DataFrame([row]))


def end_codecarbon(url, duration):
    global driver, tracker
    tracker.flush()
    tracker.stop()
    event.set()

    tmp_row = pd.read_csv('out/tmp/codecarbon.csv', nrows=1)
    row = {
        'url': url,
        'tool': 'codecarbon',
        'timestamp': tmp_row['timestamp'].values[0],
        'duration': tmp_row['duration'].values[0],
        'energy': tmp_row['energy_consumed'].values[0],
        'cpu_power': tmp_row['cpu_power'].values[0],
        'cpu_energy': tmp_row['cpu_energy'].values[0],
        'gpu_power': tmp_row['gpu_power'].values[0],
        'gpu_energy': tmp_row['gpu_power'].values[0],
        'ram_power': tmp_row['ram_power'].values[0],
        'ram_energy': tmp_row['ram_energy'].values[0],
        'emissions': tmp_row['emissions'].values[0],
        'emissions_rate': tmp_row['emissions_rate'].values[0],
    }

    output_to_csv(pd.DataFrame([row]))

    try:
        os.remove('out/tmp/codecarbon.csv')
        tracker = OfflineEmissionsTracker(measure_power_secs=duration)
        subprocess.run(['rm', '/tmp/.codecarbon.lock'])
    except Exception as e:
        print(e)


def run_codecarbon(url, duration):
    tracker.start()
    threading.Timer(duration, end_codecarbon, args=[url, duration]).start()
    event.wait()


def measure(url, duration, delay, tool: _TOOLS):
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
            case "powerjoular":
                run_powerjoular(url, duration)

    except Exception as e:
        print(f"Failed to load {url}:\n{str(e)}")


def main():
    global driver, tracker, run_id

    tool: _TOOLS = 'scaphandre'
    duration = 10  # Measurement duration
    delay = 5  # Delay between measurements
    repeat = 1
    atexit.register(tracker.stop)

    for i in range(repeat):
        run_id = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        # Measure baseline
        measure("os", duration, delay, tool)
        driver = webdriver.Firefox()
        measure("about:blank", duration, delay, tool)

        # Measure URLs
        with open('data/test.json', 'r') as f:
            urls = json.load(f)
            for url in urls:
                measure(url, duration, delay, 'codecarbon')

        driver.quit()


if __name__ == '__main__':
    main()
