import tomllib
from pathlib import Path

from pydantic import BaseModel, ValidationError

from gui import app_state


class TableContent(BaseModel):
    table: dict
    filter: dict


def generate_shared_config(state: app_state.AppState) -> dict:
    tables: dict = {}
    filters: dict = {}
    workbooks = {wb.name: {"path": wb.path} for wb in state.workbooks}

    for table in state.tables:
        with open(Path(state.dir) / "tables" / (table.id + ".toml"), "rb") as f:
            content = tomllib.load(f)
            try:
                table_content = TableContent.model_validate(content)
            except ValidationError as e:
                errs = e.errors()

                if len(errs) == 0:
                    raise Exception("Unknown validation error for table: " + table.name)

                kontak = []

                for err in errs:
                    if err["type"] == "missing":
                        kontak.append(f"Missing field: {err['loc']}")
                    else:
                        kontak.append(f"Validation error at {err['loc']}: {err['msg']}")

                raise Exception("\n".join(kontak))

        tables[table.name] = table_content.table
        tables[table.name]["workbook"] = table.workbook.name if table.workbook else ""
        filters[table.name] = table_content.filter

    return {"workbooks": workbooks, "tables": tables, "filters": filters}
