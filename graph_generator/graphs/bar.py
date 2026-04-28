import seaborn as sns

from graph_generator.dto.ToGraph import ToGraph
from graph_generator.dto.toml import Graph
from graph_generator.graphs.coverts import transform_three_axes, transform_two_axes


def make_bar_chart(data: ToGraph, config: Graph) -> None:
    match len(data.labels):
        case 1:
            ax = make_one_dimensional_chart(data, config)
        case 2:
            ax = make_two_dimensional_chart(data, config)
        case _:
            raise ValueError("Data with more than 2 dimensions is not supported.")

    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.set_title(config.title)


def make_one_dimensional_chart(data: ToGraph, config: Graph):
    df = transform_two_axes(data)

    return sns.barplot(data=df, x=config.x_axis, y="y")


def make_two_dimensional_chart(data: ToGraph, config: Graph):
    df = transform_three_axes(data)

    return sns.barplot(data=df, x=config.x_axis, y="y", hue=config.legend)
