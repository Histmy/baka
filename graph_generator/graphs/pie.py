import matplotlib.pyplot as plt

from graph_generator.dto.ToGraph import ToGraph


def make_pie_chart(data: ToGraph) -> None:
    if len(data.labels) != 1:
        raise ValueError("Pie chart requires exactly one dimension of labels.")

    plt.pie(data.data, labels=data.labels[0], autopct="%1.1f%%", startangle=90)
    plt.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle
