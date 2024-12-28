import json
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
import pandas as pd
from web_energy.utils import globals

plt.rcParams['figure.figsize'] = (10, 10)
plt.rcParams['lines.marker'] = '.'
plt.rcParams['lines.markersize'] = 10
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=['#bd0032'])
plt.rcParams['axes.xmargin'] = 0
plt.rcParams['axes.ymargin'] = 0
plt.rcParams['axes.grid'] = False
plt.rcParams['axes.formatter.use_mathtext'] = True
plt.rcParams['axes.titlepad'] = 32
plt.rcParams['axes.labelcolor'] = 'black'


def get_dataframe(tool, category, use_median=False):
    csv = os.path.join(globals.PROJECT_ROOT, 'out', 'csv', tool, f'{category}-{'median' if use_median else 'mean'}.csv')
    df = pd.read_csv(csv)
    df_no_baseline = pd.read_csv(csv, skiprows=[1, 2])

    col_energy_idx = 4
    baseline = df.iloc[1, col_energy_idx]  # 0 = os, 1 = about:blank

    # Convert from W to kWh
    multiplier = 10 / 3600 / 1000 if tool == 'scaphandre' else 1

    # Subtract baseline energy consumption from web page energy consumption
    df[df.columns[col_energy_idx]] = (df[df.columns[
        col_energy_idx]] - baseline) * multiplier
    df_no_baseline[df_no_baseline.columns[col_energy_idx]] \
        = (df_no_baseline[df_no_baseline.columns[col_energy_idx]] - baseline) * multiplier

    return df_no_baseline


def gen_barchart(df, column='energy', title=""):
    sorted_df = df.sort_values(by=column, ascending=False)

    plt.figure(figsize=(20, 10))
    plt.barh(sorted_df['url'], sorted_df[column])
    plt.xlabel('Energy Consumption (kWh)')
    plt.ylabel('URL')
    plt.title(title)

    return plt


def gen_histogram(df, column='energy', is_labeled=False, title=""):
    bin_count = 7 if is_labeled else 10
    bins = np.linspace(df[column].values.min(), df[column].values.max(), bin_count + 1)

    plt.figure()
    plt.hist(df[column], rwidth=0.85, bins=bins)
    plt.xticks(bins)
    plt.xlabel('Energy Consumption (kWh)')
    plt.ylabel('Number of URLs')
    plt.xlim(left=bins[0], right=bins[len(bins) - 1])
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.ticklabel_format(axis='y', style='plain')
    plt.title(title)

    if is_labeled:
        ax_energy = plt.gca()
        ax_label = ax_energy.secondary_xaxis(1.0)
        ax_label.set_ticks(0.5 * (bins[1:] + bins[:-1]))
        ax_label.set_xticklabels(globals.LABELS)
        ax_label.set_xlabel('Energy Labels')

    return plt


def _weighted_quantile(values, quantiles, weights):
    sorter = np.argsort(values)
    values = np.array(values)[sorter]
    weights = np.array(weights)[sorter]

    cumulative_weight = np.cumsum(weights)
    cumulative_weight /= cumulative_weight[-1]

    quantile_values = np.interp(quantiles, cumulative_weight, values)

    return pd.Series(quantile_values, index=pd.Index(quantiles, name="quantiles"))


def gen_qq(df, category, column='energy'):
    levels = np.linspace(0, 1, 8)
    quantiles = df[column].quantile(levels)

    df = df.sort_values(by=column)

    with open(os.path.join(globals.PROJECT_ROOT, 'out', 'weights', f'{category}.json'), 'r') as f:
        weights = json.load(f)

    weights = np.array(weights, dtype=np.float64)[df.index]
    weights /= weights.sum()

    weighted_quantiles = _weighted_quantile(df[column].values, levels, weights)

    plt.plot(levels, weighted_quantiles, linestyle='-', label='Weighted')
    plt.plot(levels, quantiles, linestyle=':', label='Unweighted', color='#505050', markersize=8)
    plt.legend(loc="upper left")
    plt.yticks(weighted_quantiles, [f'{q:.2f}' for q in weighted_quantiles])
    plt.gca().yaxis.set_major_formatter(plt.ScalarFormatter(useMathText=True))
    plt.gca().ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
    plt.xlabel('Theoretical Quantiles')
    plt.ylabel('Energy Consumption (kWh)')
    plt.grid(True, axis='both', linestyle=':')

    labels = []
    for i in range(len(weighted_quantiles) - 1):
        midpoint = (weighted_quantiles.iloc[i] + weighted_quantiles.iloc[i + 1]) / 2
        labels.append(midpoint)

    ax_label = plt.twinx()
    ax_label.set_yticks([
        (y - weighted_quantiles.min()) / (weighted_quantiles.max() - weighted_quantiles.min())
        for y in labels
    ])  # Normalization
    ax_label.set_yticklabels(globals.LABELS)

    return plt

