from dataclasses import dataclass
from tomllib import load
from typing import Optional

from graph_generator.dto.toml import Config, Workbook


def excel_col_to_num(col: str):
    n = 0
    for c in col.upper():
        n = n * 26 + (ord(c) - ord("A") + 1)
    return n


@dataclass
class ParsedTable:
    source_file: str
    sheet: str
    column_header: dict[str, int]
    row_header: dict[str, int]


@dataclass
class ParsedFilter:
    row: Optional[dict[str, list[str]]] = None
    column: Optional[dict[str, list[str]]] = None


def load_toml_file(file_path: str):
    """Load and parse a TOML file.

    Args:
            file_path (str): The path to the TOML file."""

    with open(file_path, "rb") as file:
        raw = load(file)

    return Config.model_validate(raw)


def load_tables(config: Config):
    if config.table:
        return {"main": config.table}

    if config.tables:
        return config.tables

    raise ValueError("No 'table' or 'tables' key found in the data.")


def load_filters(config: Config):
    if config.filter:
        return {"main": config.filter}

    if config.filters:
        return config.filters

    raise ValueError("No 'filter' or 'filters' key found in the data.")


def load_graph_config(config: Config):
    if config.graph:
        return config.graph

    raise ValueError("No 'graph' key found in the data.")


def verify_filters(tables: dict[str, ParsedTable], filters: dict[str, ParsedFilter], strict: bool = True):
    """
    Verify that each filter only references existing row and column headers.
    If strict is True, also check that each filter must have a corresponding table.
    """
    for table_name, filter in filters.items():
        if table_name not in tables:
            if strict:
                raise ValueError(f"Filter specified for table '{table_name}', but no such table found.")
            continue

        table = tables[table_name]

        if filter.row and not filter.row.keys() <= table.row_header.keys():
            raise ValueError(f"Filter for table '{table_name}' contains undefined row headers: {set(filter.row.keys()) - set(table.row_header.keys())}")

        if filter.column and not filter.column.keys() <= table.column_header.keys():
            raise ValueError(
                f"Filter for table '{table_name}' contains undefined column headers: {set(filter.column.keys()) - set(table.column_header.keys())}"
            )


def load_simple_config(file_path: str):
    data = load_toml_file(file_path)

    tables = load_tables(data)
    filters = load_filters(data)

    parsed_tables: dict[str, ParsedTable] = {}
    for table_name, table in tables.items():
        row_header = table.row_header if isinstance(table.row_header, dict) else {"default": table.row_header}
        parsed_tables[table_name] = ParsedTable(
            source_file=lookup_workbook(table.source_file, table.workbook, data.workbooks or {}),
            sheet=table.sheet,
            column_header=table.column_header if isinstance(table.column_header, dict) else {"default": table.column_header},
            row_header={key: excel_col_to_num(value) for key, value in row_header.items()},
        )

    parsed_filters: dict[str, ParsedFilter] = {}
    for filter_name, filter in filters.items():
        parsed_filters[filter_name] = ParsedFilter(
            row=filter.row if isinstance(filter.row, dict) else {"default": filter.row} if filter.row else None,
            column=filter.column if isinstance(filter.column, dict) else {"default": filter.column} if filter.column else None,
        )

    verify_filters(parsed_tables, parsed_filters)

    post_processing = data.post_processing if data.post_processing is not None else {}

    graph_config = load_graph_config(data)

    return parsed_tables, parsed_filters, post_processing, graph_config


def lookup_workbook(source_file: Optional[str], workbook: Optional[str], workbooks: dict[str, Workbook]) -> str:
    if source_file is not None:
        return source_file

    if workbook is None:
        raise ValueError("Either 'source_file' or 'workbook' must be specified for a table.")

    if workbook in workbooks:
        path = workbooks[workbook].path
        if path is None:
            raise ValueError(f"Workbook '{workbook}' does not have a 'source_file' specified.")

        return path

    raise ValueError(f"Workbook for table '{workbook}' not found.")


def deep_merge(d1, d2):
    result = dict(d1)
    for k, v in d2.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = v  # d2 overrides
    return result


def load_split_config(tables_file: str, graph_file: str):
    tables_data = load_toml_file(tables_file)
    graph_data = load_toml_file(graph_file)

    available_tables = load_tables(tables_data)
    tables: dict[str, ParsedTable] = {}

    for table in graph_data.include_tables or []:
        if table not in available_tables:
            raise ValueError(f"Included table '{table}' not found in tables configuration.")

        av = available_tables[table]

        row_header = av.row_header if isinstance(av.row_header, dict) else {"default": av.row_header}

        tables[table] = ParsedTable(
            source_file=lookup_workbook(av.source_file, av.workbook, tables_data.workbooks or {}),
            sheet=av.sheet,
            column_header=av.column_header if isinstance(av.column_header, dict) else {"default": av.column_header},
            row_header={key: excel_col_to_num(value) for key, value in row_header.items()},
        )

    # Load filters from both configurations and merge them, giving precedence to filter that apply only to the current graph
    a = load_filters(tables_data)
    b = load_filters(graph_data)
    filters: dict[str, ParsedFilter] = {}
    for key, value in (*a.items(), *b.items()):
        if key not in filters:
            filters[key] = ParsedFilter(
                row=value.row if isinstance(value.row, dict) else {"default": value.row} if value.row else None,
                column=value.column if isinstance(value.column, dict) else {"default": value.column} if value.column else None,
            )
        else:
            for attr in ["row", "column"]:
                if getattr(value, attr) is not None:
                    setattr(filters[key], attr, deep_merge(getattr(filters[key], attr) or {}, getattr(value, attr)))

    # Check if each table has a corresponding filter and vice versa
    verify_filters(tables, filters, False)

    post_processing = graph_data.post_processing if graph_data.post_processing is not None else {}

    graph_config = load_graph_config(graph_data)

    return tables, filters, post_processing, graph_config
