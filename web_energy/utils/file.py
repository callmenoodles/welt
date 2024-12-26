import os
import pandas as pd
from web_energy.utils import globals

'''
Generate one CSV file by taking the mean values in each column from a list of CSVs
'''
def gen_mean_csvs():
    path_base = os.path.join(globals.PROJECT_ROOT, 'backup', 'categories')

    for tool in globals.TOOLS:
        for category in globals.CATEGORIES:
            path = os.path.join(path_base, tool, category)

            files = []
            for file in os.listdir(path):
                if file.endswith('.csv'):
                    files.append(file)

            dataframes = []
            for file in files:
                df = pd.read_csv(os.path.join(path, file))
                dataframes.append(df)

            df_combined = pd.concat(dataframes)
            cols = ['duration', 'energy', 'cpu_power', 'cpu_energy', 'gpu_power', 'gpu_energy', 'ram_power',
                    'ram_energy', 'emissions']

            df_mean = df_combined.groupby('url', as_index=False)[cols].mean()
            headers = dataframes[0][['url', 'tool', 'timestamp', 'emissions_rate']]

            df_merged = pd.merge(headers, df_mean, on='url', how='left')
            df_merged = df_merged[[ 'url', 'tool', 'timestamp', 'duration', 'energy',
                                    'cpu_power', 'cpu_energy', 'gpu_power', 'gpu_energy',
                                    'ram_power', 'ram_energy', 'emissions', 'emissions_rate']]

            path_out = os.path.join(globals.PROJECT_ROOT, 'out', 'csv', tool, f'{category}-mean.csv')
            df_merged.to_csv(path_out, index=False)

