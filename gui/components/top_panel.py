import asyncio
from pathlib import Path

from nicegui import ui

from gui import app_state


class TopPanel:
    __state: app_state.AppState
    __dropdown: ui.select

    def __init__(self, state: app_state.AppState):
        self.__state = state

        with ui.column().classes("p-8 w-full gap-6"):
            ui.label("Control Panel").classes("text-2xl font-bold text-slate-700")
            ui.separator()

            # Dropdown
            with ui.column().classes("gap-1"):
                ui.label("Graphs").classes("text-sm font-medium text-slate-500")
                self.__dropdown = ui.select(
                    options=[],
                    on_change=self.__on_graph_change,
                ).classes("w-64")

            self.__redraw()

            self.__state.graphs.register_listener(lambda _: self.__redraw())

            # Buttons
            with ui.column().classes("gap-3"):
                ui.button(
                    "Edit",
                    icon="check_circle",  # TODO
                    on_click=self.__edit,
                ).props("unelevated").classes("bg-slate-700 text-white")

                ui.button(
                    "Delete",
                    icon="delete",
                    on_click=lambda: ui.notify("Secondary action triggered!", position="top-right"),
                ).props("outline").classes("text-slate-700")

                ui.button(
                    "Add",
                    icon="add",
                    on_click=self.__add_graph,
                ).props("outline").classes("text-slate-700")

            # TODO: add rename option

        self.__state.graphs.register_listener(lambda _: self.__redraw())

    def __redraw(self):
        self.__dropdown.options = [graph.name for graph in self.__state.graphs]
        self.__dropdown.update()

    def __add_graph(self):
        ui.notify("Add graph action triggered!", position="top-right")

        graph = app_state.Graph.new(name=f"New Graph {len(self.__state.graphs) + 1}", tables=[])
        self.__state.graphs.append(graph)

        # create file
        path = Path(self.__state.dir) / "graphs" / (graph.id + ".toml")
        with open(path, "w") as f:
            f.write("\n\n\n[graph]\n")

        # select it
        self.__state.selected_graph.set(self.__state.graphs[-1])
        self.__dropdown.value = self.__state.graphs[-1].name

    def __on_graph_change(self, e):
        self.__state.selected_graph.set(next((graph for graph in self.__state.graphs if graph.name == e.value), None))
        ui.notify(f"Selected graphhh: {e.value}", position="top-right")

    async def __edit(self):
        selected = self.__state.selected_graph.get()
        if not selected:
            ui.notify("No graph selected!", position="top-right")
            return

        path = Path(self.__state.dir) / "graphs" / (selected.id + ".toml")

        includes = ", ".join([f'"{table.name}"' for table in selected.tables])
        header = f"include_tables = [{includes}]"

        with open(path, "r+") as f:
            content = f.read()
            end_first_line = content.find("\n")
            if end_first_line != -1:
                content = header + content[end_first_line:]
            else:
                content = header
            f.seek(0)
            f.write(content)
            f.truncate()

        await asyncio.to_thread(app_state.open_file, str(path))
