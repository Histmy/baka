from tomllib import load
from graph_generator.dto.toml import Config


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


def load_config(file_path: str):
    # TODO: verify only allowed and at least required things are there
    data = load_toml_file(file_path)

    tables = load_tables(data)
    filters = load_filters(data)

    # Check if each table has a corresponding filter and vice versa
    verify_correspondence(tables, filters)

    post_processing = data.post_processing if data.post_processing is not None else {}

    graph_config = load_graph_config(data)

    return tables, filters, post_processing, graph_config
