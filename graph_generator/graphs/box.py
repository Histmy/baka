import pandas as pd
import seaborn as sns

from graph_generator.dto.ToGraph import ToGraph
from graph_generator.dto.toml import Graph


def make_box_chart(data: ToGraph, config: Graph) -> None:
    match len(data.labels):
        case 1:
            ax = make_one_dimensional_chart(data, config)
        case 2:
            ax = make_two_dimensional_chart(data, config)
        case _:
            raise ValueError("Data with more than 2 dimensions is not supported.")

    ax.set_ylim(config.min, config.max)

    if config.x_ticks_rotation is not None:
        ax.set_xticks(ax.get_xticks())
        ax.set_xticklabels(ax.get_xticklabels(), rotation=config.x_ticks_rotation)

    if config.highlight is not None:
        ax.axhline(config.highlight, color="orange", linestyle="-")

    ax.set_xlabel(config.x_description if config.x_description is not None else "")
    ax.set_ylabel(config.y_description if config.y_description is not None else "")


def make_one_dimensional_chart(data: ToGraph, config: Graph):
    df = pd.DataFrame(
        {
            "x": "data",
            "y": data.data,
        }
    )

    if config.color_palette is not None:
        sns.set_palette(config.color_palette, n_colors=1)

    return sns.boxplot(data=df, x="x", y="y")


def make_two_dimensional_chart(data: ToGraph, config: Graph):
    rows = []
    for x_label, values in zip(data.labels[0].values, data.data):
        for y in values:
            rows.append({"x": x_label, "y": y})

    df = pd.DataFrame(rows)

    if config.color_palette is not None:
        sns.set_palette(config.color_palette, n_colors=len(df["x"].unique()))

    return sns.boxplot(data=df, x="x", y="y")
