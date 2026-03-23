import numpy as np
import matplotlib.pyplot as plt
from typing import cast
from matplotlib.projections.polar import PolarAxes
from graph_generator.dto.toml import Graph
from graph_generator.dto.ToGraph import ToGraph


def make_spider_chart(data: ToGraph, config: Graph) -> None:
    _, ax = plt.subplots(figsize=(config.width, config.height), subplot_kw={"polar": True})
    ax = cast(PolarAxes, ax)  # type hint for IDE

    angles = np.linspace(0, 2 * np.pi, len(data.labels[0]), endpoint=False)
    angles = np.concatenate((angles, [angles[0]]))  # Close the plot

    ax.set_thetagrids(angles[:-1] * 180 / np.pi, data.labels[0])

    match len(data.labels):
        case 1:
            make_one_dimensional_chart(ax, angles, data)
        case 2:
            make_two_dimensional_chart(ax, angles, data)
        case _:
            raise ValueError("Data with more than 2 dimensions is not supported.")

    ax.set_title("Spider Chart")

    plt.show()
    # plt.savefig("bar_chart_seaborn.png", dpi=300, bbox_inches="tight")
    plt.close()


def make_one_dimensional_chart(ax: PolarAxes, angles: np.ndarray, data: ToGraph):
    values = data.data

    # Close the plot
    values = np.concatenate((values, [values[0]]))

    ax.plot(angles, values, marker="o")
    ax.fill(angles, values, alpha=0.25)


def make_two_dimensional_chart(ax: PolarAxes, angles: np.ndarray, data: ToGraph):
    for series_name, values in zip(data.labels[1], data.data.T):
        values = np.concatenate((values, [values[0]]))  # Close the plot
        ax.plot(angles, values, marker="o", label=series_name)
        ax.fill(angles, values, alpha=0.25)

    ax.legend(loc="upper right", bbox_to_anchor=(1.1, 1.1))
