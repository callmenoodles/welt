"""
Functions for measuring energy consumption

Repeat the experiment 10 times for optimal results
"""
import json
from uuid import uuid4

from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxWebDriver
from codecarbon import OfflineEmissionsTracker
from selenium import webdriver
from typing import Literal
import pandas as pd
import subprocess
import threading
import datetime
import os.path
import atexit
import time

t_measurement = 10  # Measurement duration
t_wait = 10  # Waiting time between measurements

driver: FirefoxWebDriver | None = None
_TOOLS = Literal["scaphandre", "codecarbon"]
filename = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
tracker: OfflineEmissionsTracker = OfflineEmissionsTracker(measure_power_secs=t_measurement)
atexit.register(tracker.stop)


def measure_baseline_with(tool: _TOOLS, run_id):
    global driver

    print("Measuring OS...")
    time.sleep(t_wait)
    measure_with(tool, t_measurement, "OS", run_id, True)

    print("Measuring Browser...")
    driver = webdriver.Firefox()
    time.sleep(t_wait)
    measure_with(tool, t_measurement, "OS + BROWSER", run_id)


def measure_with(tool: _TOOLS, duration, url: str, run_id, no_browser=False):
    def codecarbon_end():
        global driver, tracker

        tracker.flush()
        tracker.stop()
        event.set()

        row = pd.read_csv('out/codecarbon.csv', nrows=1)
        new_row = {
            'id': run_id,
            'url': url,
            'tool': tool,
            'timestamp': row['timestamp'].values[0],
            'duration': row['duration'].values[0],
            'energy': row['energy_consumed'].values[0],
            'cpu_power': row['cpu_power'].values[0],
            'cpu_energy': row['cpu_energy'].values[0],
            'gpu_power': row['gpu_power'].values[0],
            'gpu_energy': row['gpu_power'].values[0],
            'ram_power': row['ram_power'].values[0],
            'ram_energy': row['ram_energy'].values[0],
            'emissions': row['emissions'].values[0],
            'emissions_rate': row['emissions_rate'].values[0]
        }
        new_row_df = pd.DataFrame([new_row])
        outfile = 'out/out.csv'
        header = ('id,url,tool,timestamp,duration,energy,cpu_power,cpu_energy,gpu_power,gpu_energy,ram_power,'
                  'ram_energy,emissions,emissions_rate')

        if os.path.isfile(outfile):
            new_row_df.to_csv(outfile, mode='a', header=False, index=False)
        else:
            new_row_df.to_csv(outfile, header=header, index=False)

        os.remove('out/codecarbon.csv')
        tracker = OfflineEmissionsTracker(measure_power_secs=t_measurement)

    match tool:
        case "scaphandre":
            subprocess.run(
                ["scaphandre", "json", "-t", str(duration), '-f', 'out/scaphandre-' + filename + '.json'],
                capture_output=True)

        case "codecarbon":
            tracker.start()
            event = threading.Event()
            threading.Timer(t_measurement, codecarbon_end).start()
            event.wait()


def run_experiment(tool: _TOOLS):
    run_id = uuid4()
    measure_baseline_with(tool, run_id)

    with open('data/test.json', 'r') as file:
        urls = json.load(file)

        for url in urls:
            driver.get(url)
            time.sleep(t_wait)  # Wait with tracking to calibrate energy readings
            measure_with(tool, t_measurement, url, run_id)

        file.close()

    driver.quit()


run_experiment("codecarbon")
