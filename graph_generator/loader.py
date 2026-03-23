from dataclasses import dataclass
from graph_generator.dto.ToGraph import ToGraph
from graph_generator.dto.toml import Filter, Table
import openpyxl
from openpyxl.worksheet.worksheet import Worksheet
import numpy as np


@dataclass
class Bounds:
    start: int
    end: int


@dataclass
class ColumnLabels:
    x_bounds: Bounds
    y: list[int]


@dataclass
class RowLabels:
    bounds: Bounds
    x: int


@dataclass
class TableInfo:
    column_labels: ColumnLabels
    row_labels: RowLabels


def get_index_in_column(sheet: Worksheet, column: int, first_row: int, last_row: int, value: str) -> int | None:
    """Returns the index of the first occurrence of value in the specified column of the sheet.
    If the value is not found, returns None.
    """
    for row in range(first_row, last_row + 1):
        cell_value = str(sheet.cell(row=row, column=column).value)
        if cell_value == value:
            return row

    return None


def get_index_in_row(sheet: Worksheet, row: int, first_col: int, last_col: int, value: str) -> int | None:
    """Returns the index of the first occurrence of value in the specified row of the sheet.
    If the value is not found, returns None.
    """
    for col in range(first_col, last_col + 1):
        cell_value = str(sheet.cell(row=row, column=col).value)
        if cell_value == value:
            return col

    return None


def excel_col_to_num(col):
    n = 0
    for c in col.upper():
        n = n * 26 + (ord(c) - ord("A") + 1)
    return n


def craft_table_info(sheet: Worksheet, table: Table) -> TableInfo:
    key_column_number = excel_col_to_num(table.key_column)

    column_labels_x_bounds = Bounds(key_column_number + 1, key_column_number + 1)

    first_data_row = list(table.header.values())[-1] + 1

    while sheet.cell(row=first_data_row, column=column_labels_x_bounds.end + 1).value is not None:
        column_labels_x_bounds.end += 1

    column_labels_y = [i for i in table.header.values()]

    row_label = RowLabels(Bounds(first_data_row, first_data_row), key_column_number)

    while sheet.cell(row=row_label.bounds.end + 1, column=key_column_number).value is not None:
        row_label.bounds.end += 1

    return TableInfo(ColumnLabels(column_labels_x_bounds, column_labels_y), row_label)


def load_all_row_labels(sheet: Worksheet, table_info: TableInfo) -> list[str]:
    row_labels = []
    for row in range(table_info.row_labels.bounds.start, table_info.row_labels.bounds.end + 1):
        cell_value = sheet.cell(row=row, column=table_info.row_labels.x).value
        if cell_value is not None:
            row_labels.append(str(cell_value))

    return row_labels


def find_pattern_length(lst: list[str]) -> int | None:
    n = len(lst)

    if n < 2:
        return None

    first = lst[0]

    # find next occurrence of first element
    for i in range(1, n):
        if lst[i] == first:
            return i

    return None


def load_all_column_labels(sheet: Worksheet, table_info: TableInfo, row: int) -> list[str]:
    column_labels = []
    for col in range(table_info.column_labels.x_bounds.start, table_info.column_labels.x_bounds.end + 1):
        cell_value = sheet.cell(row=table_info.column_labels.y[row], column=col).value
        if cell_value is not None:
            column_labels.append(str(cell_value))

    pattern_length = find_pattern_length(column_labels)
    if pattern_length is not None:
        return column_labels[:pattern_length]

    return column_labels


def load_data(table: Table, filter: Filter) -> ToGraph:
    book = openpyxl.load_workbook(filename=table.source_file)
    sheet_num = book.sheetnames.index(table.sheet)

    if sheet_num == -1:
        raise ValueError(f"Sheet {table.sheet} not found in {table.source_file}")

    sheet = book.worksheets[sheet_num]

    table_info = craft_table_info(sheet, table)

    if filter.row_filter == "All":
        row_labels = load_all_row_labels(sheet, table_info)
    else:
        row_labels = filter.row_filter

    column_labels = []
    for i, header_row in filter.header.items():
        if header_row == "All":
            column_labels.append(load_all_column_labels(sheet, table_info, i - 1))
        else:
            column_labels.append(header_row)

    data = []

    for key in row_labels:
        row = get_index_in_column(
            sheet, table_info.row_labels.x, table_info.row_labels.bounds.start, table_info.row_labels.bounds.end, key
        )
        if row is None:
            raise ValueError(f"Row label {key} not found in table")

        data.append(traverse(sheet, row, table_info, column_labels, table_info.column_labels.x_bounds.start))

    # TODO: warn when there are non-numeric values
    return ToGraph([row_labels] + column_labels, np.array(data))


def traverse(sheet: Worksheet, row: int, table_info: TableInfo, series: list[list[str]], x: int, depth=0):
    if depth == len(series):
        return sheet.cell(row=row, column=x).value

    result = []
    for item in series[depth]:
        new_x = get_index_in_row(
            sheet, table_info.column_labels.y[depth], x, table_info.column_labels.x_bounds.end, item
        )

        if new_x is None:
            raise ValueError(f"Column label {item} not found in table")

        result.append(traverse(sheet, row, table_info, series, new_x, depth + 1))

    return result
