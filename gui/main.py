from nicegui import ui
from gui.components import right_side, toolbar
from gui.components.left_side import LeftSide
from gui.app_state import AppState, Graph, ObservableList, Table, Workbook


def build_state():
    books: ObservableList[Workbook] = ObservableList(
        [
            Workbook.new("Sales Data", "/home/hims/skola/bakalarka/data/BSc_First-year-students_RU.xlsx"),
            Workbook.new("Employee Records", "/home/hims/skola/bakalarka/data/BSc-First-year-students_UAS.xlsx"),
        ]
    )

    tables: ObservableList[Table] = ObservableList(
        [
            Table.new("Sales", books[0]),
            Table.new("Employees", books[1]),
        ]
    )

    graphs: ObservableList[Graph] = ObservableList(
        [
            Graph("Sales by Region", [tables[0]]),
            Graph("Employee Count", [tables[1]]),
        ]
    )

    return AppState(workbooks=books, tables=tables, graphs=graphs, template="ahoj", dir="/home/hims/graftest")


app_state = build_state()

# ── Shared selection state ───────────────────────────────────────────────────


toolbar.build()

# ── Left drawer – tree with tickable leaves ──────────────────────────────────

LeftSide(app_state)


# ── Main content – right panel ───────────────────────────────────────────────

right_side.build(app_state)


ui.run(title="MyApp", dark=False)
