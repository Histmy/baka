import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from graph_generator.dto.toml import Graph
from graph_generator.dto.ToGraph import ToGraph


def make_histogram_chart(data: ToGraph, config: Graph) -> None:
    plt.figure(figsize=(config.width, config.height))

    if len(data.labels) != 1:
        raise ValueError("Histogram chart requires exactly one dimension of labels.")

    ax = sns.histplot(data=data.data)

    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.set_title("Histogram Chart")

    plt.show()
    # plt.savefig("histogram_chart_seaborn.png", dpi=300, bbox_inches="tight")
    plt.close()
