"""
Functions for measuring energy consumption
"""

from codecarbon import OfflineEmissionsTracker
from selenium import webdriver
from typing import Literal
import subprocess
import threading
import datetime
import atexit
import json
import time

_TOOLS = Literal["scaphandre", "codecarbon"]
driver = webdriver.Firefox()
tracker = OfflineEmissionsTracker(country_iso_code="NLD")
atexit.register(tracker.stop)

filename = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

t_measurement = 5   # Measurement duration
t_wait = 5          # Waiting time between measurements
repeat = 5          # How many times the experiment should be repeated


def measure_baseline_with(tool: _TOOLS):
    """
    Measure energy consumption of the OS and the OS + Firefox
    """
    driver.implicitly_wait(t_wait)
    measure_with(tool, t_measurement)

    driver.get("about:blank")
    driver.implicitly_wait(t_wait)
    measure_with(tool, t_measurement)


def measure_with(tool: _TOOLS, duration, url: str):
    match tool:
        case "scaphandre":
            cmd = subprocess.run(["scaphandre", "stdout", "-t", str(duration)], capture_output=True)

            with open('out/scaphandre-' + filename, 'a') as file:
                file.write("============" + url.upper() + "============\n")
                file.write("Timestamp: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
                file.write("Measurement Duration: " + str(t_measurement) + "\n")  # Might be inaccurate
                file.write(cmd.stdout.decode())
                file.write("============" + url.upper() + "============\n\n\n")
                file.close()

        case "codecarbon":
            print("Starting tracker...")
            tracker.start()
            timer = threading.Timer(t_measurement, tracker.flush)
            timer.start()


def run_experiment(tool: _TOOLS):
    """
    Measure energy consumption using a list of websites
    """
    with open('data/test.json') as file:
        urls = json.load(file)

        for url in urls:
            driver.get(url)
            time.sleep(t_wait)
            measure_with(tool, t_measurement, url)

        file.close()

    driver.quit()
    tracker.stop()


run_experiment("scaphandre")
