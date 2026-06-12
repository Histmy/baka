import seaborn as sns

from graph_generator.dto.ToGraph import ToGraph
from graph_generator.dto.toml import Graph
from graph_generator.graphs.conversions import transform_three_axes, transform_two_axes


def make_bar_chart(data: ToGraph, config: Graph) -> None:
    match len(data.labels):
        case 1:
            ax = make_one_dimensional_chart(data, config)
        case 2:
            ax = make_two_dimensional_chart(data, config)
        case _:
            raise ValueError("Data with more than 2 dimensions is not supported.")

    ax.set_axisbelow(True)
    ax.grid(True, axis="y", color="gray", linestyle="-", linewidth=0.5, alpha=0.7)

    # TODO: is same for bar, line, box and historgram, DRY out
    ax.set_ylim(config.min, config.max)

    if config.x_ticks_rotation is not None:
        ax.set_xticks(ax.get_xticks())  # Ensure ticks are set before rotating labels
        ax.set_xticklabels(ax.get_xticklabels(), rotation=config.x_ticks_rotation)

    if config.highlight is not None:
        ax.axhline(config.highlight, color="orange", linestyle="-")

    ax.set_xlabel(config.x_description if config.x_description is not None else "")
    ax.set_ylabel(config.y_description if config.y_description is not None else "")


def make_one_dimensional_chart(data: ToGraph, config: Graph):
    df = transform_two_axes(data)

    if config.color_palette is not None:
        sns.set_palette(config.color_palette, n_colors=len(df[config.x_axis].unique()))

    if config.x_axis is None:
        raise ValueError("x_axis must be specified for one-dimensional bar chart.")

    return sns.barplot(data=df, x=config.x_axis, y="y")


def make_two_dimensional_chart(data: ToGraph, config: Graph):
    df = transform_three_axes(data)

    if config.color_palette is not None:
        sns.set_palette(config.color_palette, n_colors=len(df[config.color].unique()))

    if config.x_axis is None or config.color is None:
        raise ValueError("x_axis and color must be specified for two-dimensional bar chart.")

    return sns.barplot(data=df, x=config.x_axis, y="y", hue=config.color)
