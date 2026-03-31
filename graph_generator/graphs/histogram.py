import matplotlib.pyplot as plt
import seaborn as sns

from graph_generator.dto.ToGraph import ToGraph


def make_histogram_chart(data: ToGraph) -> None:
    if len(data.labels) != 1:
        raise ValueError("Histogram chart requires exactly one dimension of labels.")

    ax = sns.histplot(data=data.data)

    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.set_title("Histogram Chart")

    plt.show()
    # plt.savefig("histogram_chart_seaborn.png", dpi=300, bbox_inches="tight")
    plt.close()
