import pandas as pd

from graph_generator.dto.ToGraph import ToGraph


def transform_two_axes(data: ToGraph) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "x": data.labels[0],
            "y": data.data,
        }
    )


def transform_three_axes(data: ToGraph) -> pd.DataFrame:
    rows = []
    for x_label, values in zip(data.labels[0], data.data):
        for series_name, y in zip(data.labels[1], values):
            rows.append({"series": series_name, "x": x_label, "y": y})
    return pd.DataFrame(rows)


def transform_four_axes(data: ToGraph) -> pd.DataFrame:
    rows = []
    for x_label, series in zip(data.labels[0], data.data):
        for series_name, values in zip(data.labels[1], series):
            for series2_name, y in zip(data.labels[2], values):
                rows.append({"series": series_name, "series2": series2_name, "x": x_label, "y": y})
    return pd.DataFrame(rows)
