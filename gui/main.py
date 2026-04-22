from nicegui import ui

from gui.app_state import AppState, Graph, ObservableList, Table, Workbook
from gui.components import right_side
from gui.components.left_side import LeftSide
from gui.components.toolbar import Toolbar


def build_state():
    books: ObservableList[Workbook] = ObservableList([])

    tables: ObservableList[Table] = ObservableList([])

    graphs: ObservableList[Graph] = ObservableList([])

    return AppState(workbooks=books, tables=tables, graphs=graphs, template=None, dir="/hopefully/does/not/exist")


app_state = build_state()

# ── Shared selection state ───────────────────────────────────────────────────


Toolbar(app_state)

# ── Left drawer – tree with tickable leaves ──────────────────────────────────

LeftSide(app_state)


# ── Main content – right panel ───────────────────────────────────────────────

right_side.build(app_state)


ui.run(title="MyApp", dark=False)
