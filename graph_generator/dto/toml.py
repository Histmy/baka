from typing import Literal, Optional

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
    type: str

    # Generic
    width: int = 10
    height: int = 6
    title: Optional[str] = None
    color_palette: Optional[list[str]] = None
    legend_visibility: Optional[bool] = None
    legend_position: Optional[str] = None

    # Dimensional
    x_axis: Optional[str] = None
    color: Optional[str] = None
    style: Optional[str] = None

    # Only for specific graph types
    x_ticks_rotation: Optional[int] = None
    min: Optional[float] = None
    max: Optional[float] = None
    highlight: Optional[float] = None
    x_description: Optional[str] = None
    y_description: Optional[str] = None


class Workbook(BaseModel):
    path: str


class PostProcessing(BaseModel):
    join_type: Optional[Literal["sum", "ratio", "merge"]] = None
    ratio_first: Optional[str] = None
    ratio_second: Optional[str] = None
    merge_serie: Optional[str] = None
    reverse: Optional[str | list[str]] = None
    diff_serie: Optional[str] = None


class Config(BaseModel):
    workbooks: Optional[dict[str, Workbook]] = None
    table: Optional[Table] = None
    tables: Optional[dict[str, Table]] = None
    include_tables: Optional[list[str]] = None
    filter: Optional[Filter] = None
    filters: Optional[dict[str, Filter]] = None
    post_processing: Optional[PostProcessing] = None
    graph: Optional[Graph] = None
