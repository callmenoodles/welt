import json
from web_energy.utils import globals
import pandas as pd
import numpy as np
import os

'''
Output JSON file with mean, median, min, max, and standard deviation for each category
'''
def generate(column='energy'):
    for tool in globals.TOOLS:
        res = {}
        path = os.path.join(globals.PROJECT_ROOT, 'backup', 'categories', tool)

        for root, categories, files in os.walk(path):
            for category in categories:
                path_category = os.path.join(root, category)
                values = []
                count = 0

                for file in os.listdir(path_category):
                    path_file = os.path.join(path_category, file)
                    df = pd.read_csv(path_file)
                    count = df.shape[0]

                    values.extend(df[column].dropna().tolist())

                res[category] = {
                    "count": count-2,
                    "mean": float(np.mean(values)),
                    "median": float(np.median(values)),
                    "min": float(np.min(values)),
                    "max": float(np.max(values)),
                    "sd": float(np.std(values))
                }

        json_obj = json.dumps(res, indent=2)
        path_out = os.path.join(globals.PROJECT_ROOT, 'out', 'stats')

        if not os.path.exists(path_out):
            os.makedirs(path_out)

        with open(os.path.join(path_out, f'{tool}.json'), 'w') as f:
            f.write(json_obj)