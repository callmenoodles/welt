"""
Visualize data from Scaphandre and CodeCarbon
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

color = "#66a85a"


def create_histogram(df, column):
    plt.figure(figsize=(10, 6))
    plt.hist(df[column], color=color, rwidth=0.8)  # A-G
    plt.title("Energy Consumption Distribution of Landing Pages", pad=32)
    plt.xlabel('Energy Consumption (kWh)', labelpad=16)
    plt.ylabel('Frequency', labelpad=16)
    plt.ticklabel_format(style='sci', scilimits=(0, 0))
    plt.grid(False)


def create_labeled_histogram(df, column):
    bins = np.linspace(df[column].values.min(), df[column].values.max(), 8)
    labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

    plt.figure(figsize=(10, 6))
    plt.hist(df[column], color=color, rwidth=0.8, bins=bins)
    plt.xticks(bins)
    plt.title("Energy Consumption Distribution of Landing Pages", pad=32)
    plt.xlabel('Energy Consumption (kWh)', labelpad=16)
    plt.ylabel('Frequency', labelpad=16)
    plt.ticklabel_format(style='sci', scilimits=(0, 0))
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
    plt.barh(sorted_df['url'], sorted_df[column], color=color)
    plt.xlabel('Energy Consumption (kWh)')
    plt.ylabel('URL')
    plt.title('Energy Consumption of Web Pages')
    plt.ticklabel_format(axis='x', style='sci', scilimits=(0, 0))


if __name__ == '__main__':
    dataframe = pd.read_csv('out/out.csv')
    col = 'energy'

    create_histogram(dataframe, col)
    create_labeled_histogram(dataframe, col)
    create_barchart(dataframe, col)

    plt.show()
