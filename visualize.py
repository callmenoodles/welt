"""
Visualize data from Scaphandre and CodeCarbon
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

color = "#bd0032"
color_uva = "#bd0032"


def create_histogram(df, column):
    plt.figure(figsize=(10, 6))
    plt.hist(df[column], color=color_uva, rwidth=0.8)  # A-G
    plt.title("Energy Consumption Distribution of Landing Pages", pad=32)
    plt.xlabel('Energy Consumption (kWh)', labelpad=16)
    plt.ylabel('Frequency', labelpad=16)
    plt.ticklabel_format(axis='x', style='sci', scilimits=(0, 0))
    plt.grid(False)


def create_labeled_histogram(df, column):
    bins = np.linspace(df[column].values.min(), df[column].values.max(), 8)
    labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

    plt.figure(figsize=(10, 6))
    plt.hist(df[column], color=color_uva, rwidth=0.8, bins=bins)
    plt.xticks(bins)
    plt.title("Energy Consumption Distribution of Landing Pages", pad=32)
    plt.xlabel('Energy Consumption (kWh)', labelpad=16)
    plt.ylabel('No. Pages', labelpad=16)
    plt.ticklabel_format(axis='x', style='sci', scilimits=(0, 0))
    plt.xlim(left=bins[0], right=bins[len(bins) - 1])
    plt.grid(True)

    energy_axis = plt.gca()
    label_axis = energy_axis.secondary_xaxis(1.0)
    label_axis.set_ticks(0.5 * (bins[1:] + bins[:-1]))
    label_axis.set_xticklabels(labels)
    label_axis.set_xlabel('Energy Labels', labelpad=16)


def create_barchart(df, column):
    sorted_df = df.sort_values(by=column, ascending=False)

    plt.figure(figsize=(10, 6))
    plt.barh(sorted_df['url'], sorted_df[column], color=color_uva)
    plt.xlabel('Energy Consumption (kWh)')
    plt.ylabel('URL')
    plt.title('Energy Consumption of Web Pages')
    plt.ticklabel_format(axis='x', style='sci', scilimits=(0, 0))


def create_quantile(df, column):
    lvl_equal = np.linspace(0, 1, 8)
    quantiles = df[column].quantile(lvl_equal)

    plt.plot(lvl_equal, quantiles, marker='o', linestyle='-', color=color_uva)

    for i in range(len(quantiles) - 1):
        plt.axhline(quantiles.iloc[i], color='gray', linestyle='--', alpha=0.5)
        plt.axhline(quantiles.iloc[i+1], color='gray', linestyle='--', alpha=0.5)

    plt.yticks(quantiles.values, [f"{q:.2f}" for q in quantiles])
    plt.title(f'Quantile Plot for Energy Consumption')
    plt.margins(x=0, y=0)
    plt.xlabel('Quantile')
    plt.ylabel(column)
    plt.grid(False)

    labelax = plt.twinx()
    labelax.set_yticks([])
    labels = [(quantiles.iloc[i] + quantiles.iloc[i + 1]) / 2 for i in range(len(quantiles) - 1)]
    labelax.set_yticks([(y - quantiles.min()) / (quantiles.max() - quantiles.min()) for y in labels])
    labelax.set_yticklabels([f"{chr(65 + i)}" for i in range(len(labels))], color='black')


def plot_file(path):
    df = pd.read_csv(path)
    df_nobase = pd.read_csv(path, skiprows=[1, 2])
    energy_col = 4
    baseline = df.iloc[1, energy_col]  # 0 = os, 1 = about:blank

    df[df.columns[energy_col]] = df[df.columns[energy_col]] - baseline
    df_nobase[df_nobase.columns[energy_col]] = df_nobase[df_nobase.columns[energy_col]] - baseline

    col = 'energy'

    create_quantile(df_nobase, col)
    create_histogram(df_nobase, col)
    create_barchart(df_nobase, col)


# Create CSV file with average values per category
def avg_csv(category, out):
    csvs = [file for file in os.listdir(category) if file.endswith('.csv')]
    dfs = []

    for csv_file in csvs:
        df = pd.read_csv(os.path.join(category, csv_file))
        dfs.append(df)

    combined = pd.concat(dfs)
    cols = ['duration', 'energy', 'cpu_power', 'cpu_energy', 'gpu_power', 'gpu_energy', 'ram_power', 'ram_energy',
            'emissions']

    mean = combined.groupby('url', as_index=False)[cols].mean()

    path = os.path.join(category, csvs[0])
    df = pd.read_csv(path)

    headers = df[['url', 'tool', 'timestamp', 'emissions_rate']]

    res = pd.merge(headers, mean, on='url', how='left')
    res = res[['url', 'tool', 'timestamp', 'duration', 'energy', 'cpu_power', 'cpu_energy', 'gpu_power', 'gpu_energy',
               'ram_power', 'ram_energy', 'emissions', 'emissions_rate']]

    res.to_csv(out, index=False)
    plot_file(out)


if __name__ == '__main__':
    # path = filedialog.askdirectory(title='Choose Directory')
    path = os.path.join('backup', 'categories', 'scaphandre', 'marketing')
    avg_csv(path, os.path.join('out', os.path.basename(path) + '.csv'))

    plt.show()
