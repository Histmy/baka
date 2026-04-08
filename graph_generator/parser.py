from dataclasses import dataclass
from tomllib import load
from typing import Optional

from graph_generator.dto.toml import Config, Filter, Sheet
from graph_generator.dto.toml import Table as TableConfig


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


def verify_correspondence(tables: dict, filters: dict):
    table_keys = set(tables.keys())
    filter_keys = set(filters.keys())

    if table_keys != filter_keys:
        missing_in_filters = table_keys - filter_keys
        missing_in_tables = filter_keys - table_keys

        error_messages = []
        if missing_in_filters:
            s = "s" if len(missing_in_filters) > 1 else ""
            error_messages.append(f"Filter{s} missing for table{s}: {', '.join(missing_in_filters)}")
        if missing_in_tables:
            s = "s" if len(missing_in_tables) > 1 else ""
            error_messages.append(f"Table{s} missing for filter{s}: {', '.join(missing_in_tables)}")

        raise ValueError("Correspondence check failed: " + "; ".join(error_messages))


def verify_filters(tables: dict[str, TableConfig], filters: dict[str, Filter]):
    missing = []
    for table in tables:
        if table not in filters:
            missing.append(table)

    if missing:
        s = "s" if len(missing) > 1 else ""
        raise ValueError(f"Filter{s} missing for table{s}: {', '.join(missing)}")


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

    # Check if each table has a corresponding filter and vice versa
    verify_correspondence(tables, filters)

    post_processing = data.post_processing if data.post_processing is not None else {}

    graph_config = load_graph_config(data)

    return parsed_tables, filters, post_processing, graph_config


def lookup_workbook(source_file: Optional[str], workbook: Optional[str], sheets: dict[str, Sheet]) -> str:
    if source_file is not None:
        return source_file

    if workbook is None:
        raise ValueError("Either 'source_file' or 'workbook' must be specified for a table.")

    if workbook in sheets:
        path = sheets[workbook].path
        if path is None:
            raise ValueError(f"Worksheet '{workbook}' does not have a 'source_file' specified.")

        return path

    raise ValueError(f"Worksheet for table '{workbook}' not found.")


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
    filters = a
    for key, value in b.items():
        if key not in filters:
            filters[key] = value
        else:
            for attr in ["row", "column"]:
                if getattr(value, attr) is not None:
                    setattr(filters[key], attr, deep_merge(getattr(filters[key], attr) or {}, getattr(value, attr)))

    # Check if each table has a corresponding filter and vice versa
    verify_filters(available_tables, filters)

    post_processing = graph_data.post_processing if graph_data.post_processing is not None else {}

    graph_config = load_graph_config(graph_data)

    return tables, filters, post_processing, graph_config
