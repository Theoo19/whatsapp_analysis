import wordcloud
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends import backend_pdf
from matplotlib import dates as mdates
from math import pi, floor
import pandas as pd


def radar_chart(categories, datasets, names, ticks_amount=4, r_min=None, r_max=None, title=None):
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    if title is not None:
        ax.set_title(title)
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)
    ax.set_rlabel_position(0)

    r_min = min(min(data_set) for data_set in datasets) if r_min is None else r_min
    if r_max is None:
        r_max = max(max(data_set) for data_set in datasets)
        r_step = (r_max - r_min) / (10 * (ticks_amount - 2))
    else:
        r_step = 0
    r_ticks = np.linspace(r_min, r_max + r_step, ticks_amount)
    angles = np.linspace(0, 2 * pi, len(categories) + 1)

    ax.set_xticks(angles[:-1], categories)
    ax.set_rticks(r_ticks[:-1], color="grey", size=7)
    ax.set_rlim(r_ticks[0], r_ticks[-1])

    for dataset, name in zip(datasets, names):
        dataset.append(dataset[0])
        ax.plot(angles, dataset, label=name)
        ax.fill(angles, dataset, alpha=0.2)
    ax.legend()
    return fig, ax


def save_figs(data_sets):
    """

    :param data_sets:
    :type data_sets: list of pd.DataFrame
    :return:
    :rtype:
    """
    with backend_pdf.PdfPages("output.pdf") as pdf:
        for data_set in data_sets:
            figure = plt.figure()
            plt.plot(data_set)
            pdf.savefig(figure)
        pdf.savefig()


def get_figure_1(dataframe, title=None, x_label=None, y_label=None, show_legend=None, show_grid=True,):
    show_legend = len(dataframe.columns.values) > 1 if show_legend is None else show_legend

    fig, ax = plt.subplots(figsize=(8.3, 5.8))
    if title is not None:
        ax.set_title(title)
    if x_label is not None:
        ax.set_xlabel(x_label)
    if y_label is not None:
        ax.set_ylabel(y_label)
    ax.grid(axis="y", visible=show_grid, zorder=0)

    ticks_amount = min(10, len(dataframe.index.values))
    ticks_spacing = floor((len(dataframe.index.values) - 1) / (ticks_amount - 1))
    x_ticks = list(dataframe.index.values[ticks_spacing * i] for i in range(ticks_amount))

    for column in dataframe.columns.values:
        ax.plot(dataframe[column], label=column, zorder=3)
        ax.fill_between(dataframe.index.values, dataframe[column], alpha=0.7, zorder=3)

    ax.set_xticks(x_ticks)
    ax.set_xlim(dataframe.index.values[0], dataframe.index.values[-1])
    ax.set_ylim(bottom=0)

    if show_legend:
        ax.legend()

    return fig, ax


def get_figure_date(dataframe):
    fig, ax = get_figure_1(dataframe, "Messages per date", y_label="Messages", show_grid=True)
    fig.autofmt_xdate()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m-%Y"))
    return fig, ax


def get_figure_days(dataframe):
    datasets = list(dataframe[column].tolist() for column in dataframe.columns.values)
    return radar_chart(dataframe.index.values, datasets, dataframe.columns.values, r_min=0,
                       title="Messages per weekday")


def word_cloud(frequencies):
    cloud = wordcloud.WordCloud(width=1920, height=1080, min_font_size=20, background_color="white")
    return cloud.generate_from_frequencies(frequencies)
