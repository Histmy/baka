from pathlib import Path
import tomllib

import docx

from gui.AppState import AppState
from word_replace.main import replace_placeholder_with_figure


def generate_shared_config(state: AppState):
    tables = {}
    filters = {}
    workbooks = {workbook.name: {"path": workbook.path} for workbook in state.workbooks}

    for table in state.tables:
        with open(Path(state.dir) / "tables" / (table.name + ".toml"), "rb") as f:
            content = tomllib.load(f)
            tables[table.name] = content["table"]
            tables[table.name]["workbook"] = table.workbook.name if table.workbook else ""

            filters[table.name] = content["filters"]

    return {
        "workbooks": workbooks,
        "tables": tables,
        "filters": filters,
    }


def fill_template(template_path: str, output_path: str, graphs_path: Path):
    doc = docx.Document(template_path)

    replace_placeholder_with_figure(doc, graphs_path, "Figure", "Figure", "This is a sample figure.")

    doc.save(output_path)
