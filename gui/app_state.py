import os
import subprocess
import sys
import time
import tomllib
import uuid
from pathlib import Path
from typing import Generic, Optional, TypeVar

import tomli_w
from attr import asdict, dataclass


def generate_uuid7() -> uuid.UUID:
    """Generates a UUIDv7."""
    timestamp_ms = int(time.time() * 1000)
    random_bytes = os.urandom(10)

    uuid_bytes = bytearray(timestamp_ms.to_bytes(6, byteorder="big") + random_bytes)

    uuid_bytes[6] = (uuid_bytes[6] & 0x0F) | 0x70
    uuid_bytes[8] = (uuid_bytes[8] & 0x3F) | 0x80

    # Cast the UUID object to a string before returning
    return uuid.UUID(bytes=bytes(uuid_bytes))


def open_file(path: str):
    if sys.platform == "win32":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.run(["open", path])
    else:
        subprocess.run(["xdg-open", path])


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
    id: str
    name: str
    tables: list[Table]

    @classmethod
    def new(cls, name: str, tables: list[Table]):
        return cls(id=str(generate_uuid7()), name=name, tables=tables)


class SelectedGraph:
    def __init__(self) -> None:
        self.__graph: Optional[Graph] = None
        self.__listeners: list = []

    def set(self, graph: Optional[Graph]):
        self.__graph = graph
        self.__notify()

    def get(self) -> Optional[Graph]:
        return self.__graph

    def register(self, callback):
        self.__listeners.append(callback)

    def __notify(self):
        for callback in self.__listeners:
            callback()


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

    def extend(self, items):
        super().extend(items)
        self._notify()

    def clear(self):
        super().clear()
        self._notify()

    def _notify(self):
        for callback in self._listeners:
            callback(self)

    def register_listener(self, callback):
        self._listeners.append(callback)


class ObservableOptionalString:
    def __init__(self, value: str | None):
        self._value = value
        self._listeners = []

    def set(self, value: str | None):
        self._value = value
        self._notify()

    def get(self) -> str | None:
        return self._value

    def _notify(self):
        for callback in self._listeners:
            callback(self._value)

    def register_listener(self, callback):
        self._listeners.append(callback)


class AppState:
    workbooks: ObservableList[Workbook]
    tables: ObservableList[Table]
    graphs: ObservableList[Graph]
    template = ObservableOptionalString(None)
    dir: str

    selected_graph = SelectedGraph()

    def __init__(self, dir: str):
        self.workbooks = ObservableList()
        self.tables = ObservableList()
        self.graphs = ObservableList()
        self.template = ObservableOptionalString(None)
        self.dir = dir
        self.selected_graph = SelectedGraph()

    def reset(self, dir: str):
        self.workbooks.clear()
        self.tables.clear()
        self.graphs.clear()
        self.template = ObservableOptionalString(None)
        self.dir = dir
        self.selected_graph.set(None)

    def save(self):
        if self.dir is None:
            raise ValueError("No directory specified for saving the project.")

        data = {
            "workbooks": [asdict(workbook) for workbook in self.workbooks],
            "tables": [{"id": table.id, "name": table.name, "workbook": table.workbook.id if table.workbook else ""} for table in self.tables],
            "graphs": [{"id": graph.id, "name": graph.name, "tables": [table.id for table in graph.tables]} for graph in self.graphs],
            "template": self.template.get() or "",
        }

        with open(Path(self.dir) / "config.toml", "wb") as f:
            tomli_w.dump(data, f)

    def load(self, path: str):
        with open(Path(path) / "config.toml", "rb") as f:
            data = tomllib.load(f)

        self.workbooks.clear()
        self.workbooks.extend(Workbook(**workbook) for workbook in data.get("workbooks", []))

        self.tables.clear()
        for table in data.get("tables", []):
            workbook = next(wb for wb in self.workbooks if wb.id == table["workbook"])
            self.tables.append(Table(id=table["id"], name=table["name"], workbook=workbook))

        self.graphs.clear()
        for graph in data.get("graphs", []):
            tables = [t for t in self.tables if t.id in graph["tables"]]
            self.graphs.append(Graph(id=graph["id"], name=graph["name"], tables=tables))

        self.template.set(data.get("template", None))
        self.dir = path
