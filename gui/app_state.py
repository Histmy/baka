# Map of id -> label for every leaf node (populated while building the tree)
import os
import time
import uuid

from attr import asdict, dataclass
from pathlib import Path
import tomli_w
import tomllib
from typing import Optional, TypeVar, Generic


def generate_uuid7() -> uuid.UUID:
    """Generates a UUIDv7 and returns it as a TOML-serializable string."""

    timestamp_ms = int(time.time() * 1000)
    random_bytes = os.urandom(10)

    uuid_bytes = bytearray(timestamp_ms.to_bytes(6, byteorder="big") + random_bytes)

    uuid_bytes[6] = (uuid_bytes[6] & 0x0F) | 0x70
    uuid_bytes[8] = (uuid_bytes[8] & 0x3F) | 0x80

    # Cast the UUID object to a string before returning
    return uuid.UUID(bytes=bytes(uuid_bytes))


@dataclass
class Workbook:
    id: str
    name: str
    path: str

    @classmethod
    def new(cls, name: str, path: str):
        return cls(id=str(generate_uuid7()), name=name, path=path)


@dataclass
class Table:
    id: str
    name: str
    workbook: Workbook

    @classmethod
    def new(cls, name: str, workbook: Workbook):
        return cls(id=str(generate_uuid7()), name=name, workbook=workbook)


@dataclass
class Graph:
    name: str
    tables: list[Table]


class SelectedGraph:
    __graph: Optional[Graph] = None
    __listeners: list = []

    def set(self, graph: Optional[Graph]):
        self.__graph = graph
        self.__notify()

    def get(self) -> Optional[Graph]:
        return self.__graph

    def register(self, callback):
        self.__listeners.append(callback)

    def __notify(self):
        for callback in self.__listeners:
            callback(self.__graph)


T = TypeVar("T")


class ObservableList(list[T], Generic[T]):
    def __init__(self, *args):
        super().__init__(*args)
        self._listeners = []

    def append(self, item):
        super().append(item)
        self._notify()

    def remove(self, item):
        super().remove(item)
        self._notify()

    def _notify(self):
        for callback in self._listeners:
            callback(self)

    def register_listener(self, callback):
        self._listeners.append(callback)


@dataclass
class AppState:
    workbooks: ObservableList[Workbook]
    tables: ObservableList[Table]
    graphs: ObservableList[Graph]
    template: Optional[str]
    dir: str

    selected_graph: SelectedGraph = SelectedGraph()

    def save(self, path: str):
        data = {
            "workbooks": [asdict(workbook) for workbook in self.workbooks],
            "tables": [{"name": table.name, "workbook": table.workbook.name if table.workbook else ""} for table in self.tables],
            "graphs": [{"name": graph.name, "tables": [table.name for table in graph.tables]} for graph in self.graphs],
            "template": self.template if self.template else "",
        }

        with open(Path(path) / "config.toml", "wb") as f:
            tomli_w.dump(data, f)

    @classmethod
    def load(cls, path: str):
        with open(Path(path) / "config.toml", "rb") as f:
            data = tomllib.load(f)

        workbooks = ObservableList(Workbook(**workbook) for workbook in data.get("workbooks", []))

        tables = ObservableList(
            [Table.new(name=table["name"], workbook=next((wb for wb in workbooks if wb.name == table["workbook"]))) for table in data.get("tables", [])]
        )

        graphs = ObservableList(
            [
                Graph(name=graph["name"], tables=[next((table for table in tables if table.name == table_name)) for table_name in graph["tables"]])
                for graph in data.get("graphs", [])
            ]
        )

        return cls(workbooks=workbooks, tables=tables, graphs=graphs, template=data.get("template") or None, dir=path)
