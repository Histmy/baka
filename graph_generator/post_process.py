from typing import Callable

import numpy as np

from graph_generator.dto.ToGraph import Label, ToGraph


class PostProcess:
    @staticmethod
    def collapse(data: ToGraph) -> ToGraph:
        labels: list[Label] = []

        for label in data.labels:
            if len(label.values) != 1:
                labels.append(label)

        return ToGraph(labels, data.data.squeeze())

    @staticmethod
    def simple_transpose(data: ToGraph) -> ToGraph:
        if len(data.labels) != 2:
            raise ValueError("Expected exactly 2 levels of labels for simple transpose")

        return ToGraph([data.labels[1], data.labels[0]], data.data.T)

    @staticmethod
    def diff(data: ToGraph, serie: str) -> ToGraph:
        """
        Computes the difference between the first and the last element of the specified series.
        """

        serie_index = next((i for i, label in enumerate(data.labels) if label.name == serie), None)

        if serie_index is None:
            raise ValueError(f"Serie '{serie}' not found in data")

        new_labels = data.labels.copy()
        new_labels[serie_index] = Label(name=serie, values=["diff"])
        new_data = np.empty([len(label.values) for label in new_labels], dtype=np.float32)

        index_src: list[slice | int] = [slice(None)] * len(data.data.shape)
        index_dest: list[slice | int] = [slice(None)] * len(data.data.shape)
        for i in range(data.data.shape[serie_index]):
            index_src[serie_index] = i
            index_dest[serie_index] = 0

            new_data[tuple(index_dest)] = data.data[tuple(index_src)][-1] - data.data[tuple(index_src)][0]

        return ToGraph(new_labels, new_data)

    @staticmethod
    def sum(data_one: ToGraph, data_two: ToGraph) -> None:
        """
        Sums two data collections by modifiing the first one.
        It assumes the series structure is identical for both collections
        """

        data_one.data += data_two.data

    @staticmethod
    def divide(data_one: ToGraph, data_two: ToGraph) -> None:
        """
        Divides two data collections by modifiing the first one.
        It assumes the series structure is identical for both collections
        """

        data_one.data /= data_two.data

    @staticmethod
    def merge(data_one: ToGraph, data_two: ToGraph, serie: str, labeler_one: Callable[[str], str], labeler_two: Callable[[str], str]) -> None:
        """
        Merges two data collections by modifiing the first one.
        It assumes the series structure is identical for both collections
        """

        serie_index = next((i for i, label in enumerate(data_one.labels) if label.name == serie), None)

        if serie_index is None:
            raise ValueError(f"Serie '{serie}' not found in data_one")

        labels_one_copy = data_one.labels.copy()
        data_one.labels = []
        for label_one, label_two in zip(labels_one_copy, data_two.labels):
            if label_one.name != serie:
                data_one.labels.append(label_one)
                continue

            lbl = Label(name=serie, values=[])
            for i in range(len(label_one.values)):
                lbl.values.append(labeler_one(label_one.values[i]))
                lbl.values.append(labeler_two(label_two.values[i]))

            data_one.labels.append(lbl)

        new_data = np.empty([len(label.values) for label in data_one.labels], dtype=np.float32)

        step = new_data.shape[serie_index] // data_two.data.shape[serie_index]

        # Copy data from data_one and data_two interleaved
        index_src: list[slice | int] = [slice(None)] * len(data_one.data.shape)
        index_dest: list[slice | int] = [slice(None)] * len(data_two.data.shape)
        for i in range(data_two.data.shape[serie_index]):
            index_src[serie_index] = i
            index_dest[serie_index] = step * i

            new_data[tuple(index_dest)] = data_one.data[tuple(index_src)]

            index_dest[serie_index] = step * i + 1
            new_data[tuple(index_dest)] = data_two.data[tuple(index_src)]

        data_one.data = new_data
