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
    def diff(data: ToGraph, serie: str) -> ToGraph:
        """
        Computes the difference between the first and the last element of the specified series.
        """

        serie_index = next((i for i, label in enumerate(data.labels) if label.name == serie), None)

        if serie_index is None:
            raise ValueError(f"Serie '{serie}' not found in data")

        if serie_index == 0:
            labels = [Label(name=serie, values=["diff"])]
            new_data = np.array([((data.data[-1] - data.data[0]) / data.data[0])], dtype=np.float32)
            return ToGraph(labels, new_data)

        new_labels = data.labels.copy()
        new_labels[serie_index] = Label(name=serie, values=["diff"])
        new_data = np.empty([len(label.values) for label in new_labels], dtype=np.float32)

        index: list[slice | int] = [slice(None)] * len(data.data.shape)
        for i in range(data.data.shape[serie_index - 1]):
            index[serie_index - 1] = i

            new_data[tuple(index)][0] = (data.data[tuple(index)][-1] - data.data[tuple(index)][0]) / data.data[tuple(index)][0]

        return ToGraph(new_labels, new_data)

    @staticmethod
    def sum(data_one: ToGraph, data_two: ToGraph, serie: str) -> ToGraph:
        """
        Sums two data collections by modifiing the first one.
        It assumes the series structure is identical for both collections
        """

        serie_index = next((i for i, label in enumerate(data_one.labels) if label.name == serie), None)

        if serie_index is None:
            raise ValueError(f"Serie '{serie}' not found in data_one")

        if data_one.data.shape[serie_index] <= data_two.data.shape[serie_index]:
            smaller = data_one
            bigger = data_two
        else:
            smaller = data_two
            bigger = data_one

        index_bigger: list[slice | int] = [slice(None)] * len(bigger.data.shape)
        index_smaller: list[slice | int] = [slice(None)] * len(smaller.data.shape)
        for i in bigger.labels[serie_index].values:
            if i not in smaller.labels[serie_index].values:
                continue

            index_bigger[serie_index] = bigger.labels[serie_index].values.index(i)
            index_smaller[serie_index] = smaller.labels[serie_index].values.index(i)

            bigger.data[tuple(index_bigger)] += smaller.data[tuple(index_smaller)]

        return bigger

    @staticmethod
    def divide(data_one: ToGraph, data_two: ToGraph, serie: str) -> None:
        """
        Divides two data collections by modifiing the first one.
        It assumes the series structure is identical for both collections
        """
        serie_index = next((i for i, label in enumerate(data_one.labels) if label.name == serie), None)

        if serie_index is None:
            raise ValueError(f"Serie '{serie}' not found in data_one")

        index_one: list[slice | int] = [slice(None)] * len(data_one.data.shape)
        index_two: list[slice | int] = [slice(None)] * len(data_two.data.shape)
        for i in data_one.labels[serie_index].values:
            if i not in data_two.labels[serie_index].values:
                continue

            index_one[serie_index] = data_one.labels[serie_index].values.index(i)
            index_two[serie_index] = data_two.labels[serie_index].values.index(i)

            data_one.data[tuple(index_one)] /= data_two.data[tuple(index_two)]

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

            labels = [(labeler_one, label) for label in label_one.values] + [(labeler_two, label) for label in label_two.values]
            labels.sort(key=lambda x: x[1])

            data_one.labels.append(Label(name=serie, values=[labeler(label) for labeler, label in labels]))

        new_data = np.empty([len(label.values) for label in data_one.labels], dtype=np.float32)

        step = new_data.shape[serie_index] // data_two.data.shape[serie_index]

        # Copy data from data_one and data_two interleaved
        index_src1: list[slice | int] = [slice(None)] * len(data_one.data.shape)
        index_dest: list[slice | int] = [slice(None)] * len(data_two.data.shape)
        for i in range(len(labels_one_copy[serie_index].values)):
            index_dest[serie_index] = data_one.labels[serie_index].values.index(labeler_one(labels_one_copy[serie_index].values[i]))

            index_src1[serie_index] = i
            new_data[tuple(index_dest)] = data_one.data[tuple(index_src1)]

        index_src2: list[slice | int] = [slice(None)] * len(data_two.data.shape)
        for i in range(len(data_two.labels[serie_index].values)):
            index_dest[serie_index] = data_one.labels[serie_index].values.index(labeler_two(data_two.labels[serie_index].values[i]))

            index_src2[serie_index] = i
            new_data[tuple(index_dest)] = data_two.data[tuple(index_src2)]

        data_one.data = new_data

    @staticmethod
    def reverse(data: ToGraph, series: list[str]) -> None:
        """
        Reverses the order of values in the specified series.
        """

        for serie in series:
            serie_index = next((i for i, label in enumerate(data.labels) if label.name == serie), None)

            if serie_index is None:
                raise ValueError(f"Serie '{serie}' not found in data")

            data.labels[serie_index].values.reverse()
            data.data = np.flip(data.data, axis=serie_index)
