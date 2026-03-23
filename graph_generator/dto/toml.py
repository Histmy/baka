from typing import Literal, Optional
from pydantic import BaseModel


class Table(BaseModel):
    source_file: str
    sheet: str
    key_column: str
    header: dict[int, int]


class Filter(BaseModel):
    row_filter: list[str] | Literal["All"]
    header: dict[int, list[str] | Literal["All"]]


class Graph(BaseModel):
    title: str
    type: str
    width: int = 10
    height: int = 6


class Config(BaseModel):
    table: Optional[Table] = None
    tables: Optional[dict[str, Table]] = None
    filter: Optional[Filter] = None
    filters: Optional[dict[str, Filter]] = None
    post_processing: Optional[dict] = None
    graph: Optional[Graph] = None
