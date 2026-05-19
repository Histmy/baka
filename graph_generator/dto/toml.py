from typing import Optional

from pydantic import BaseModel


class Table(BaseModel):
    source_file: Optional[str] = None
    workbook: Optional[str] = None
    sheet: str
    column_header: dict[str, int]
    row_header: dict[str, str]


class Filter(BaseModel):
    row: Optional[dict[str, list[str]]] = None
    column: Optional[dict[str, list[str]]] = None


class Graph(BaseModel):
    title: str
    type: str
    width: int = 10
    height: int = 6
    x_axis: Optional[str] = None
    legend: Optional[str] = None
    style: Optional[str] = None


class Workbook(BaseModel):
    path: str


class Config(BaseModel):
    workbooks: Optional[dict[str, Workbook]] = None
    table: Optional[Table] = None
    tables: Optional[dict[str, Table]] = None
    include_tables: Optional[list[str]] = None
    filter: Optional[Filter] = None
    filters: Optional[dict[str, Filter]] = None
    post_processing: Optional[dict] = None
    graph: Optional[Graph] = None
