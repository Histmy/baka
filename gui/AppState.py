from dataclasses import asdict, dataclass
import tomllib
import tomli_w
from typing import Optional
from pathlib import Path


@dataclass
class Workbook:
    name: str
    path: Optional[str]


@dataclass
class Table:
    name: str
    workbook: Optional[Workbook]
    stuff: str


@dataclass
class Graph:
    name: str
    tables: list[Table]


@dataclass
class AppState:
    workbooks: list[Workbook]
    tables: list[Table]
    graphs: list[Graph]
    template: Optional[str]
    dir: str

    def save(self, path: str):
        data = {
            "workbooks": [asdict(workbook) for workbook in self.workbooks],
            "tables": [{"name": table.name, "workbook": table.workbook.name if table.workbook else "", "stuff": table.stuff} for table in self.tables],
            "graphs": [{"name": graph.name, "tables": [table.name for table in graph.tables]} for graph in self.graphs],
            "template": self.template if self.template else "",
        }

        with open(Path(path) / "config.toml", "wb") as f:
            tomli_w.dump(data, f)

    def load(self, path: str):
        with open(Path(path) / "config.toml", "rb") as f:
            data = tomllib.load(f)

        self.dir = path

        self.workbooks = [Workbook(**workbook) for workbook in data.get("workbooks", [])]

        self.tables = [
            Table(name=table["name"], workbook=next((wb for wb in self.workbooks if wb.name == table["workbook"]), None), stuff=table["stuff"])
            for table in data.get("tables", [])
        ]

        self.graphs = [
            Graph(name=graph["name"], tables=[next((table for table in self.tables if table.name == table_name)) for table_name in graph["tables"]])
            for graph in data.get("graphs", [])
        ]

        self.template = data.get("template") or None
