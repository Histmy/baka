import matplotlib.pyplot as plt
import seaborn as sns

from graph_generator.dto.ToGraph import ToGraph
from graph_generator.dto.toml import Graph


def make_pie_chart(data: ToGraph, config: Graph) -> None:
    if len(data.labels) != 1:
        raise ValueError("Pie chart requires exactly one dimension of labels.")

    if config.color_palette is not None:
        sns.set_palette(config.color_palette, n_colors=len(data.labels[0].values))

    plt.pie(data.data, labels=data.labels[0].values, autopct="%1.1f%%", startangle=90)
    plt.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle
