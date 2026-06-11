from typing import cast

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.projections.polar import PolarAxes

from graph_generator.dto.ToGraph import ToGraph
from graph_generator.dto.toml import Graph


def make_spider_chart(data: ToGraph, config: Graph) -> None:
    _, ax = plt.subplots(figsize=(config.width, config.height), subplot_kw={"polar": True})
    ax = cast(PolarAxes, ax)  # type hint for MyPy

    angles = np.linspace(0, 2 * np.pi, len(data.labels[0].values), endpoint=False)
    angles = np.concatenate((angles, [angles[0]]))  # Close the plot

    ax.set_thetagrids(angles[:-1] * 180 / np.pi, data.labels[0].values)

    match len(data.labels):
        case 1:
            make_one_dimensional_chart(ax, angles, data)
        case 2:
            make_two_dimensional_chart(ax, angles, data, config)
        case _:
            raise ValueError("Data with more than 2 dimensions is not supported.")


def make_one_dimensional_chart(ax: PolarAxes, angles: np.ndarray, data: ToGraph):
    values = data.data

    # Close the plot
    values = np.concatenate((values, [values[0]]))

    ax.plot(angles, values, marker="o")
    ax.fill(angles, values, alpha=0.25)


def make_two_dimensional_chart(ax: PolarAxes, angles: np.ndarray, data: ToGraph, config: Graph):

    if config.x_axis is None or config.color is None:
        raise ValueError("x_axis and color must be specified for two-dimensional spider chart.")

    if data.labels[0].name == config.x_axis:
        top_data = data.data.T
        top = 1
        bottom = 0
    else:
        top_data = data.data
        top = 0
        bottom = 1

    for series_name, values in zip(data.labels[top].values, top_data):
        values = np.concatenate((values, [values[bottom]]))  # Close the plot
        ax.plot(angles, values, marker="o", label=series_name)
        ax.fill(angles, values, alpha=0.25)
