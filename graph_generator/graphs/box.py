import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from graph_generator.dto.ToGraph import ToGraph


def make_box_chart(data: ToGraph) -> None:
    match len(data.labels):
        case 1:
            ax = make_one_dimensional_chart(data)
        case 2:
            ax = make_two_dimensional_chart(data)
        case _:
            raise ValueError("Data with more than 2 dimensions is not supported.")

    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.set_title("Box Chart")

    plt.show()
    # plt.savefig("box_chart_seaborn.png", dpi=300, bbox_inches="tight")
    plt.close()


def make_one_dimensional_chart(data: ToGraph):
    df = pd.DataFrame(
        {
            "x": "data",
            "y": data.data,
        }
    )

    return sns.boxplot(data=df, x="x", y="y")


def make_two_dimensional_chart(data: ToGraph):
    rows = []
    for x_label, values in zip(data.labels[0], data.data):
        for y in values:
            rows.append({"x": x_label, "y": y})

    df = pd.DataFrame(rows)

    return sns.boxplot(data=df, x="x", y="y")
