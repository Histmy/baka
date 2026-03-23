from graph_generator.dto.ToGraph import ToGraph


def collapse(data: ToGraph) -> ToGraph:
    labels = []

    for label in data.labels:
        if not isinstance(label, list):
            raise ValueError("Expected label to be a list")

        if len(label) != 1:
            labels.append(label)

    return ToGraph(labels, data.data.squeeze())


def simple_transpose(data: ToGraph) -> ToGraph:
    if len(data.labels) != 2:
        raise ValueError("Expected exactly 2 levels of labels for simple transpose")

    return ToGraph([data.labels[1], data.labels[0]], data.data.T)
