# Configuration of graphs

A graph is generated from a `TOML` file(s). It may either be a single file containing the table definition and filtering with the settings specific to the graph, or it may be generated from a file containing definitons of the tables and their generic filtering, and a separate file, that includes tables from this file, may optionally add or override any filters for those tables and define the graph settings.

## Sections of the graph configuration

Each graph configuration is split into three sections: Table definition, filtering and graph settings. There may also be an optional section for workbook definition. Each of those is described in more detail below.

### Workbook definition

If a single Excel workbook contains multiple source tables it may be useful to define the workbook in a separate `[workbooks]` section. Each workbook must be named and defines only the path to the file.

Example:

```toml
[workbooks.one]
path = "path/to/workbook.xlsx"

[workbooks.two]
path = "path/to/workbook2.xlsx"
```

### Table definitions

If user wants to specify just one table, they can define it in a section `[table]`. Otherwise they must name each table and define them in section `[tables]`, like `[tables.Table1]`, `[tables.Table2]` etc.

Tables may either include the path to the workbook they are located in, or they may refer to a workbook defined in the `[workbooks]` section. They must also specify the sheet name where the table is located.

Each table has to define at least one row header and at least one column header. Row and column headers are named for later filtering. They are defined as either the row number of column letter where the header is located.

Example:

```toml
[table]
source_file = "path/to/workbook.xlsx"
row_header = "A"
column_header = 1
```
or

```toml
[table.one]
workbook = "one"
sheet = "Sheet1"
row_header = "A"
column_header = 1

[table.two]
workbook = "two"
sheet = "Sheet2"
row_header = "B"
column_header.year = 2
column_header.month = 3
```

### Filtering

Each table can (and should) be filtered to include only the relevant data for the graph. Filtering is done by defining the filters for any row and/or column headers. If there is only one table defined by the `[table]` section, the filter must be defined in the `[filter]` section. If there are multiple tables defined by the `[tables]` section, the filter for each table must be defined in the corresponding section, like `[filters.one]`, `[filters.two]` etc.

Example:

```toml
[filter]
row_header = ["Row1", "Row2", "Row3"]
column_header = ["Column1", "Column2"]
```
or

```toml
[filters.one]
row_header = ["Row1", "Row2", "Row3"]
column_header.year = [2020, 2021]
column_header.month = ["January", "February"]

[filters.two]
row_header.name = ["RowA", "RowB"]
column_header = ["ColumnX", "ColumnY", "ColumnZ"]
```

### Graph settings

So far graphs can be only configured to be of a specific type and must inlcude a title, but this is soon to be changed. These graph settings must be defined in the `[graph]` section.

Example:

```toml
[graph]
type = "bar"
title = "My Graph"
```
or

```toml
[graph]
type = "line"
title = "My Line Graph"
```

## Single file graph configuration

All of the above sections may be defined in a single file, as long as they are properly named and structured. There must be at least one table definition and exactly one graph definition.

Example:

```toml
[workbooks.one]
path = "path/to/workbook.xlsx"

[table]
workbook = "one"
sheet = "Sheet1"
row_header = "A"
column_header = 1

[filter]
row_header = ["Row1", "Row2", "Row3"]
column_header = ["Column1", "Column2"]

[graph]
type = "bar"
title = "My Graph"
```

## Split file graph configuration

The graph configuration may also be split into two files: one for the table definitions and filtering, and another for the graph settings. The first file is meant to be shared across multiple graphs, while the second file is meant to be specific to a single graph.

The graph file must specify what tables to include from the first file, and may also add or override any filters for those tables.

Example of the first file:

```toml
[workbooks.one]
path = "path/to/workbook.xlsx"

[workbooks.two]
path = "path/to/workbook2.xlsx"

[tables.Table1]
workbook = "one"
sheet = "Sheet1"
row_header = "A"
column_header = 1

[tables.Table2]
workbook = "two"
sheet = "Sheet2"
row_header = "B"
column_header.year = 2
column_header.month = 3

[filters.Table1]
row_header = ["Row1", "Row2", "Row3"]
column_header = ["Column1", "Column2"]
```

Example of the second file:

```toml
include_tables = ["Table1", "Table2"]

[filters.Table2]
row_header.name = ["RowA", "RowB"]
column_header = ["ColumnX", "ColumnY", "ColumnZ"]

[graph]
type = "line"
title = "My Line Graph"
```

## Differences in the GUI

In the GUI for the graph definitions, the user specifies the workbooks, tables with filters and each graph in different files.

The workbooks follow the same structure as described above.

The tables, since they are each defined separately, are defined in the `[table]` and `[filter]` sections, but are given a name in the text field. They are then automatically processed as if they were defined in the `[tables]` and `[filters]` sections, with the name given in the text field.

The graph definition also follows the same structure as described above in the split file configuration.
