import json

import pandas as pd
import numpy as np
import os

'''
Output JSON file with mean, median, min, max, and standard deviation for each category
'''


def stats(col, path):
    res = {}

    for root, categories, files in os.walk(path):
        for category in categories:
            category_path = os.path.join(root, category)
            values = []
            count = 0

            for file in os.listdir(category_path):
                file_path = os.path.join(category_path, file)
                df = pd.read_csv(file_path)
                count = df.shape[0]

                values.extend(df[col].dropna().tolist())

            res[category] = {
                "count": count,
                "mean": float(np.mean(values)),
                "median": float(np.median(values)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
                "sd": float(np.std(values))
            }

    return res


def main():
    res = json.dumps({
        'codecarbon': stats('energy', os.path.join('backup', 'categories', 'codecarbon')),
        'scaphandre': stats('energy', os.path.join('backup', 'categories', 'scaphandre'))
    }, indent=2)

    with open(os.path.join('out', 'stats.json'), 'w') as f:
        f.write(res)


if __name__ == '__main__':
    main()
