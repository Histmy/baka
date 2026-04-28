import numpy as np

from graph_generator.dto.ToGraph import Label, ToGraph


def collapse(data: ToGraph) -> ToGraph:
    labels: list[Label] = []

    for label in data.labels:
        if len(label.values) != 1:
            labels.append(label)

    return ToGraph(labels, data.data.squeeze())


def simple_transpose(data: ToGraph) -> ToGraph:
    if len(data.labels) != 2:
        raise ValueError("Expected exactly 2 levels of labels for simple transpose")

    return ToGraph([data.labels[1], data.labels[0]], data.data.T)


def combine(datas: list[ToGraph]) -> ToGraph:
    if len(datas) == 0:
        raise ValueError("No data to combine")

    labels = []
    data_arrays = []

    for data in datas:
        labels.append(data.labels)
        data_arrays.append(data.data)

    combined_labels = [label for sublist in labels for label in sublist]
    combined_data = np.concatenate(data_arrays, axis=0)

    return ToGraph(combined_labels, combined_data)
