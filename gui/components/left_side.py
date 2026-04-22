import asyncio
from pathlib import Path
from tkinter import filedialog
from typing import Literal, Optional

from nicegui import ui

from gui import app_state


class LeftSide:
    __state: app_state.AppState
    __tree: ui.tree
    __selected_type: Literal["workbook", "table"] | None = None
    __selected_id: str | None

    def __init__(self, state: app_state.AppState):
        self.__state = state
        self.__leaf_labels = {}
        self.__selected_id = None
        self.__selected_type = None

        with ui.left_drawer(value=True, bordered=True).classes("bg-slate-50 p-2"):
            with ui.row().classes("w-full"):
                ui.button(icon="add", on_click=self.__add_workbook).classes("text-slate-400")
                ui.button(icon="add", on_click=self.__add_table).classes("text-slate-400")
                ui.button(icon="edit", on_click=self.__edit).classes("ml-auto text-slate-400")
                ui.button(icon="delete", on_click=self.__delete_selected).classes("text-slate-400")

            ui.separator().classes("my-2")

            self.__build_tree()  # type: ignore - pylance is confused by the @ui.refreshable decorator

            self.__state.selected_graph.register(self.__on_graph_change)

            self.__state.workbooks.register_listener(lambda _: self.__build_tree.refresh())
            self.__state.tables.register_listener(lambda _: self.__build_tree.refresh())

    @ui.refreshable
    def __build_tree(self):
        tree_nodes = []

        for workbook in self.__state.workbooks:
            children = []
            for table in self.__state.tables:
                if table.workbook and table.workbook.name == workbook.name:
                    self.__leaf_labels[table.id] = table.name
                    children.append({"id": table.id, "label": table.name, "icon": "table_chart"})
            tree_nodes.append({"id": workbook.id, "label": workbook.name, "icon": "table_view", "children": children})

        # Collect leaf id -> label for chip rendering later
        for parent in tree_nodes:
            for child in parent.get("children", []):
                self.__leaf_labels[child["id"]] = child["label"]

        expanded_ids = [node["id"] for node in tree_nodes]

        def select(e):
            self.__selected_id = e.value

            if e.value in [workbook.id for workbook in self.__state.workbooks]:
                self.__selected_type = "workbook"
            else:
                self.__selected_type = "table"

        self.__tree = (
            ui.tree(
                nodes=tree_nodes,
                node_key="id",
                label_key="label",
                on_tick=self.__on_tick,
                tick_strategy="leaf",
                on_select=select,
            )
            .props(f"expanded={expanded_ids}")
            .classes("w-full")
        )

        selected_graph = self.__state.selected_graph.get()
        if selected_graph:
            self.__select_selected(selected_graph)

    def __select_selected(self, graph: app_state.Graph):
        self.__tree.untick()  # Clear all ticks first

        table_ids = set(table.id for table in graph.tables)
        ticked_ids = [table_id for table_id in self.__leaf_labels if table_id in table_ids]
        self.__tree.tick(ticked_ids)

    def __on_tick(self, e):
        selected_graph = self.__state.selected_graph.get()
        if not selected_graph:
            return

        selected_tables = set()
        for node_id in e.value or []:
            if node_id in self.__leaf_labels:
                selected_tables.add(node_id)

        selected_graph.tables = [table for table in self.__state.tables if table.id in selected_tables]

    def __on_graph_change(self, graph: Optional[app_state.Graph]):
        if graph is not None:
            self.__select_selected(graph)

    async def __add_workbook(self):
        path = await asyncio.to_thread(filedialog.askopenfilename, filetypes=[("Excel files", "*.xlsx *.xls")])
        if not path:
            return

        self.__state.workbooks.append(app_state.Workbook.new(name=f"New Workbook {len(self.__state.workbooks) + 1}", path=path))

        self.__build_tree.refresh()

    def __add_table(self):
        selected = self.__selected_id
        if not selected or self.__selected_type != "workbook":
            return

        # TODO: name
        table = app_state.Table.new(name=f"New Table {len(self.__state.tables) + 1}", workbook=next(wb for wb in self.__state.workbooks if wb.id == selected))
        self.__state.tables.append(table)

        # create file
        path = Path(self.__state.dir) / "tables" / (table.id + ".toml")
        with open(path, "w") as f:
            f.write("[table]\n\n[filters]")

        self.__build_tree.refresh()

    async def __edit(self):
        if not self.__selected_id or self.__selected_type != "table":
            return

        path = Path(self.__state.dir) / "tables" / (self.__selected_id + ".toml")

        await asyncio.to_thread(app_state.open_file, str(path))

    def __delete_selected(self):
        if not self.__selected_id or not self.__selected_type:
            return

        if self.__selected_type == "workbook":
            self.__state.workbooks.remove(next(wb for wb in self.__state.workbooks if wb.id == self.__selected_id))

            # also remove all tables that belong to this workbook
            for table in [table for table in self.__state.tables if table.workbook.id == self.__selected_id]:
                self.__state.tables.remove(table)
        else:
            self.__state.tables.remove(next(t for t in self.__state.tables if t.id == self.__selected_id))

        self.__build_tree.refresh()
