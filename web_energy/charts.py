import json
import os
import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from web_energy.utils import globals

root = tk.Tk()
root.withdraw()

color_uva = '#bd0032'
hline_color = 'gray'
hline_alpha = 0.2
hline_style = '--'

plt.rcParams['figure.figsize'] = (10, 10)
plt.rcParams['lines.marker'] = '.'
plt.rcParams['lines.markersize'] = 10
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=[color_uva])  # UvA red
plt.rcParams['axes.xmargin'] = 0
plt.rcParams['axes.ymargin'] = 0
plt.rcParams['axes.grid'] = False
plt.rcParams['axes.formatter.use_mathtext'] = True
plt.rcParams['axes.formatter.limits'] = (-0, 0)
plt.rcParams['axes.titlepad'] = 32
plt.rcParams['axes.labelcolor'] = 'black'

tools = ['codecarbon', 'scaphandre']
categories = ['age_restricted', 'bakery', 'content_sharing', 'country_select', 'e_commerce', 'informational',
              'login', 'marketing', 'online_games', 'search_engines', 'social_media', 'software_distribution',
              'streaming_audio', 'streaming_video']

def gen_barchart(df, column='energy', title=""):
    sorted_df = df.sort_values(by=column, ascending=False)

    plt.figure()
    plt.barh(sorted_df['url'], sorted_df[column])
    plt.xlabel('Energy Consumption (kWh)')
    plt.ylabel('Web Page (URL)')
    plt.title(title)


def gen_histogram(df, column='energy', title=""):
    plt.figure()
    plt.hist(df[column], rwidth=0.85)
    plt.xlabel('Energy Consumption (kWh)')
    plt.ylabel('Frequency')
    plt.title(title)


def gen_histogram_labeled(df, column='energy'):
    bins = np.linspace(df[column].values.min(), df[column].values.max(), 8)
    labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

    plt.hist(df[column], rwidth=0.85, bins=bins)
    plt.xticks(bins)
    plt.xlabel('Energy Consumption (kWh)')
    plt.ylabel('No. Pages')
    plt.xlim(left=bins[0], right=bins[len(bins) - 1])

    ax_energy = plt.gca()
    ax_label = ax_energy.secondary_xaxis(1.0)
    ax_label.set_ticks(0.5 * (bins[1:] + bins[:-1]))
    ax_label.set_xticklabels(labels)
    ax_label.set_xlabel('Energy Labels')


def gen_qq(df, column='energy'):
    levels = np.linspace(0, 1, 8)
    quantiles = df[column].quantile(levels)

    # FIXME: Duplicate: Combine with gen_qq_weighted
    for i in range(len(quantiles) - 1):
        plt.axhline(quantiles.iloc[i], color=hline_color, linestyle=hline_style, alpha=hline_alpha)
        plt.axhline(quantiles.iloc[i+1], color=hline_color, linestyle=hline_style, alpha=hline_alpha)

    plt.plot(levels, quantiles, linestyle='-', label='Unweighted')
    plt.legend(loc="upper left")
    plt.yticks(quantiles.values, [f'{q:.2f}' for q in quantiles])
    plt.xlabel('Theoretical Quantiles')
    plt.ylabel('Energy Consumption (kWh)')
    plt.grid(True, axis='x', linestyle='--')

    labels = []
    for i in range(len(quantiles) - 1):
        midpoint = (quantiles.iloc[i] + quantiles.iloc[i + 1]) / 2
        labels.append(midpoint)

    ax_label = plt.twinx()
    ax_label.set_yticks([(y - quantiles.min()) / (quantiles.max() - quantiles.min()) for y in labels])  # normalize
    ax_label.set_yticklabels(globals.LABELS)


def weighted_quantile(values, quantiles, weights):
    sorter = np.argsort(values)
    values = np.array(values)[sorter]
    weights = np.array(weights)[sorter]

    cumulative_weight = np.cumsum(weights)
    cumulative_weight /= cumulative_weight[-1]

    return np.interp(quantiles, cumulative_weight, values)


def gen_qq_weighted(df, category, column='energy'):
    levels = np.linspace(0, 1, 8)
    df = df.sort_values(by=column)

    with open(os.path.join(globals.PROJECT_ROOT, 'out', 'weights', f'{category}.json'), 'r') as f:
        weights = json.load(f)

    weights = np.array(weights, dtype=np.float64)[df.index]
    weights /= weights.sum()

    quantiles = weighted_quantile(df[column].values, levels, weights)

    # FIXME: Duplicate: Combine with gen_qq_weighted
    for i in range(len(quantiles) - 1):
        plt.axhline(quantiles[i], color=hline_color, linestyle=hline_style, alpha=hline_alpha)
        plt.axhline(quantiles[i + 1], color=hline_color, linestyle=hline_style, alpha=hline_alpha)

    plt.plot(levels, quantiles, linestyle='-', label='Weighted')
    plt.legend(loc="upper left")
    plt.yticks(quantiles, [f'{q:.2f}' for q in quantiles])
    plt.xlabel('Theoretical Quantiles')
    plt.ylabel('Energy Consumption (kWh)')
    plt.grid(True, axis='x', linestyle='--')

    labels = []
    for i in range(len(quantiles) - 1):
        midpoint = (quantiles[i] + quantiles[i + 1]) / 2
        labels.append(midpoint)

    ax_label = plt.twinx()
    ax_label.set_yticks([(y - quantiles.min()) / (quantiles.max() - quantiles.min()) for y in labels])  # normalize
    ax_label.set_yticklabels(globals.LABELS)


def main():
    category = 'informational'
    tool = 'scaphandre'

    # TODO: Median
    csv = os.path.join(globals.PROJECT_ROOT, 'out', 'csv', tool, f'{category}-mean.csv')
    df = pd.read_csv(csv)
    df_no_baseline = pd.read_csv(csv, skiprows=[1, 2])

    # Subtract baseline energy consumption from web page energy consumption
    col_energy_idx = 4
    baseline = df.iloc[1, col_energy_idx]  # 0 = os, 1 = about:blank
    df[df.columns[col_energy_idx]] = df[df.columns[col_energy_idx]] - baseline
    df_no_baseline[df_no_baseline.columns[col_energy_idx]] \
        = df_no_baseline[df_no_baseline.columns[col_energy_idx]] - baseline

    # Graphs
    gen_barchart(df_no_baseline)

    # plt.savefig(os.path.join(globals.PROJECT_ROOT, 'out', 'graphs', 'test.png'))
    plt.show()


if __name__ == '__main__':
    main()