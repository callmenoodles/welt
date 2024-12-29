from web_energy.utils import globals
import json
from selenium import webdriver
import pandas as pd
import os

def _get_page_size_bytes(url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.set_capability("goog:loggingPrefs", {'performance': 'ALL'})
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--disk-cache-size=0')

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    total_bytes = 0
    for entry in driver.get_log('performance'):
        try:
            log = json.loads(entry['message'])['message']

            if log['method'] == 'Network.dataReceived':
                total_bytes += log['params']['encodedDataLength']

        except (KeyError, json.JSONDecodeError) as e:
            print(e)

    driver.quit()
    return total_bytes

'''
Get the size of the web pages in bytes to use as weights in a weighted quantile plot 
'''
def measure_page_sizes():
    for category in globals.CATEGORIES:
        df = pd.read_csv(os.path.join(globals.PROJECT_ROOT, 'out', f'{category}.csv'))
        urls = df.loc[2:, 'url'].tolist()

        weights = []
        for url in urls:
            size = _get_page_size_bytes(url)
            weights.append(size)

        with open(os.path.join(globals.PROJECT_ROOT, 'out', 'weights', f'{category}.json'), 'w') as f:
            json.dump(weights, f)
