from dataclasses import dataclass
from typing import Optional


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
