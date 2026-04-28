import seaborn as sns

from graph_generator.dto.ToGraph import ToGraph
from graph_generator.dto.toml import Graph
from graph_generator.graphs.coverts import transform_four_axes, transform_three_axes, transform_two_axes


def make_line_chart(data: ToGraph, config: Graph) -> None:
    match len(data.labels):
        case 1:
            ax = make_one_dimensional_chart(data, config)
        case 2:
            ax = make_two_dimensional_chart(data, config)
        case 3:
            ax = make_three_dimensional_chart(data, config)
        case _:
            raise ValueError("Data with more than 2 dimensions is not supported.")

    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.set_title("Line Chart")


def make_one_dimensional_chart(data: ToGraph, config: Graph):
    df = transform_two_axes(data)

    return sns.lineplot(data=df, x=config.x_axis, y="y")


def make_two_dimensional_chart(data: ToGraph, config: Graph):
    df = transform_three_axes(data)

    return sns.lineplot(data=df, x=config.x_axis, y="y", hue=config.legend)


def make_three_dimensional_chart(data: ToGraph, config: Graph):
    df = transform_four_axes(data)

    return sns.lineplot(data=df, x=config.x_axis, y="y", hue=config.legend, style=config.style)
