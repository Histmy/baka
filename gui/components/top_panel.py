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
                    on_change=self.on_graph_change,
                ).classes("w-64")

            self.redraw()

            self.__state.graphs.register_listener(lambda _: self.redraw())

            # Buttons
            with ui.column().classes("gap-3"):
                ui.button(
                    "Edit",
                    icon="check_circle",  # TODO
                    on_click=lambda: ui.notify("Primary action triggered!", color="positive", position="top-right"),
                ).props("unelevated").classes("bg-slate-700 text-white")

                ui.button(
                    "Delete",
                    icon="delete",
                    on_click=lambda: ui.notify("Secondary action triggered!", position="top-right"),
                ).props("outline").classes("text-slate-700")

                ui.button(
                    "Add",
                    icon="add",
                    on_click=self.add_graph,
                ).props("outline").classes("text-slate-700")

            # TODO: add rename option

    def redraw(self):
        self.__dropdown.options = [graph.name for graph in self.__state.graphs]
        self.__dropdown.update()

    def add_graph(self):
        ui.notify("Add graph action triggered!", position="top-right")

        self.__state.graphs.append(app_state.Graph(name=f"New Graph {len(self.__state.graphs) + 1}", tables=[]))

        # select it
        self.__state.selected_graph.set(self.__state.graphs[-1])
        self.__dropdown.value = self.__state.graphs[-1].name

    def on_graph_change(self, e):
        self.__state.selected_graph.set(next((graph for graph in self.__state.graphs if graph.name == e.value), None))
        ui.notify(f"Selected graphhh: {e.value}", position="top-right")
