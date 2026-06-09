import pandas as pd

from graph_generator.dto.ToGraph import ToGraph


def transform_two_axes(data: ToGraph) -> pd.DataFrame:
    first_label = data.labels[0]

    return pd.DataFrame(
        {
            first_label.name: first_label.values,
            "y": data.data,
        }
    )


def transform_three_axes(data: ToGraph) -> pd.DataFrame:
    rows = []
    for x_label, values in zip(data.labels[0].values, data.data):
        for series_name, y in zip(data.labels[1].values, values):
            rows.append({data.labels[1].name: series_name, data.labels[0].name: x_label, "y": y})
    return pd.DataFrame(rows)


def transform_four_axes(data: ToGraph) -> pd.DataFrame:
    rows = []
    for x_label, series in zip(data.labels[0].values, data.data):
        for series_name, values in zip(data.labels[1].values, series):
            for series2_name, y in zip(data.labels[2].values, values):
                rows.append({data.labels[1].name: series_name, data.labels[2].name: series2_name, data.labels[0].name: x_label, "y": y})
    return pd.DataFrame(rows)
