import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from graph_generator.dto.toml import Graph
from graph_generator.dto.ToGraph import ToGraph
from graph_generator.graphs.coverts import transform_three_axes, transform_two_axes


def make_bar_chart(data: ToGraph, config: Graph) -> None:
    plt.figure(figsize=(config.width, config.height))

    match len(data.labels):
        case 1:
            ax = make_one_dimensional_chart(data)
        case 2:
            ax = make_two_dimensional_chart(data)
        case _:
            raise ValueError("Data with more than 2 dimensions is not supported.")

    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.set_title("Bar Chart")

    plt.show()
    # plt.savefig("bar_chart_seaborn.png", dpi=300, bbox_inches="tight")
    plt.close()


def make_one_dimensional_chart(data: ToGraph):
    df = transform_two_axes(data)

    return sns.barplot(data=df, x="x", y="y")


def make_two_dimensional_chart(data: ToGraph):
    df = transform_three_axes(data)

    return sns.barplot(data=df, x="x", y="y", hue="series")
