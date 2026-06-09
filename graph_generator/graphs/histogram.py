import seaborn as sns

from graph_generator.dto.ToGraph import ToGraph
from graph_generator.dto.toml import Graph


def make_histogram_chart(data: ToGraph, config: Graph) -> None:
    if len(data.labels) != 1:
        raise ValueError("Histogram chart requires exactly one dimension of labels.")

    ax = sns.histplot(data=data.data)

    if config.color_palette is not None:
        sns.set_palette(config.color_palette, n_colors=1)

    ax.set_ylim(config.min, config.max)

    if config.x_ticks_rotation is not None:
        ax.set_xticks(ax.get_xticks())
        ax.set_xticklabels(ax.get_xticklabels(), rotation=config.x_ticks_rotation)

    if config.highlight is not None:
        ax.axhline(config.highlight, color="orange", linestyle="-")

    ax.set_xlabel(config.x_description if config.x_description is not None else "")
    ax.set_ylabel(config.y_description if config.y_description is not None else "")
