from nicegui import ui

from gui import app_state


class LeftSide:
    __state: app_state.AppState
    __tree: ui.tree

    def __init__(self, state: app_state.AppState):
        self.__state = state
        self.__leaf_labels = {}

        with ui.left_drawer(value=True, bordered=True).classes("bg-slate-50 p-2"):
            with ui.row().classes("w-full"):
                ui.label("Navigation").classes("text-xs font-semibold text-slate-400 uppercase px-2 pt-2 pb-1")
                ui.button(icon="add", on_click=self.add_workbook).classes("ml-auto text-slate-400")

            self.__build_tree()  # type: ignore - pylance is confused by the @ui.refreshable decorator

            self.__state.selected_graph.register(self.on_graph_change)

    @ui.refreshable
    def __build_tree(self):
        tree_nodes = []

        for workbook in self.__state.workbooks:
            children = []
            for table in self.__state.tables:
                if table.workbook and table.workbook.name == workbook.name:
                    leaf_id = table.id
                    self.__leaf_labels[leaf_id] = table.name
                    children.append({"id": leaf_id, "label": table.name, "icon": "table_chart"})
            tree_nodes.append({"id": f"workbook:{workbook.name}", "label": workbook.name, "icon": "table_view", "children": children})

        # Collect leaf id -> label for chip rendering later
        for parent in tree_nodes:
            for child in parent.get("children", []):
                self.__leaf_labels[child["id"]] = child["label"]

        expanded_ids = [node["id"] for node in tree_nodes]

        self.__tree = (
            ui.tree(
                nodes=tree_nodes,
                node_key="id",
                label_key="label",
                on_tick=self.on_tick,
                tick_strategy="leaf",
            )
            .props(f"expanded={expanded_ids}")
            .classes("w-full")
        )

        selected_graph = self.__state.selected_graph.get()
        if selected_graph:
            self.select_selected(selected_graph)

    def select_selected(self, graph: app_state.Graph):
        self.__tree.untick()  # Clear all ticks first

        table_ids = set(table.id for table in graph.tables)
        ticked_ids = [table_id for table_id in self.__leaf_labels if table_id in table_ids]
        self.__tree.tick(ticked_ids)

    def on_tick(self, e):
        selected_graph = self.__state.selected_graph.get()
        if not selected_graph:
            return

        selected_tables = set()
        for node_id in e.value or []:
            if node_id in self.__leaf_labels:
                selected_tables.add(node_id)

        selected_graph.tables = [table for table in self.__state.tables if table.id in selected_tables]

    def on_graph_change(self, graph: app_state.Graph):
        self.select_selected(graph)

    def add_workbook(self):
        self.__state.workbooks.append(app_state.Workbook.new(name=f"New Workbook {len(self.__state.workbooks) + 1}", path=""))  # TODO: name

        self.__build_tree.refresh()
