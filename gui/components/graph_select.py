from pathlib import Path

import flet as ft

from gui import app_state
from gui.components.dialogs.rename_graph import RenameGraph


class GraphSelect:
    """Graph selection and management panel."""

    def __init__(self, page: ft.Page, state: app_state.AppState):
        self._page = page
        self._state = state

        self._dropdown = ft.Dropdown(
            label="Graphs",
            width=260,
            options=[],
        )

        self._dropdown.on_select = self._on_graph_change

        state.graphs.register_listener(lambda _: self._redraw())

    # ── public widget ─────────────────────────────────────────────────────────

    def build(self) -> ft.Container:
        self._redraw()

        return ft.Container(
            padding=ft.padding.all(24),
            content=ft.Column(
                [
                    ft.Divider(),
                    self._dropdown,
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "Edit",
                                icon=ft.Icons.EDIT,
                                bgcolor=ft.Colors.BLUE_GREY_800,
                                color=ft.Colors.WHITE,
                                on_click=self._edit,
                            ),
                            ft.ElevatedButton(
                                "Rename",
                                icon=ft.Icons.DRIVE_FILE_RENAME_OUTLINE,
                                bgcolor=ft.Colors.BLUE_GREY_800,
                                color=ft.Colors.WHITE,
                                on_click=self._rename,
                            ),
                            ft.OutlinedButton(
                                "Delete",
                                icon=ft.Icons.DELETE,
                                on_click=self._delete_graph,
                            ),
                            ft.OutlinedButton(
                                "Add",
                                icon=ft.Icons.ADD,
                                on_click=self._add_graph,
                            ),
                        ],
                        spacing=8,
                        wrap=True,
                    ),
                ],
                spacing=16,
            ),
        )

    # ── internals ─────────────────────────────────────────────────────────────

    def _redraw(self):
        self._dropdown.options = [ft.dropdown.Option(g.name) for g in self._state.graphs]
        # Keep current selection if it still exists
        current = self._dropdown.value
        if current not in [g.name for g in self._state.graphs]:
            self._dropdown.value = None
        self._page.update()

    def _add_graph(self):
        n = len(self._state.graphs) + 1
        graph = app_state.Graph.new(name=f"New Graph {n}", tables=[])
        self._state.graphs.append(graph)

        path = Path(self._state.dir) / "graphs" / (graph.id + ".toml")
        path.write_text("\n\n\n[graph]\n")

        self._state.selected_graph.set(graph)
        self._dropdown.value = graph.name
        self._page.update()

    def _delete_graph(self):
        selected = self._state.selected_graph.get()
        if not selected:
            self._snack("No graph selected!")
            return
        self._state.graphs.remove(selected)
        self._state.selected_graph.set(None)
        self._dropdown.value = None
        self._page.update()

    def _on_graph_change(self, e):
        graph = next((g for g in self._state.graphs if g.name == e.control.value), None)
        self._state.selected_graph.set(graph)

    def _edit(self):
        selected = self._state.selected_graph.get()
        if not selected:
            self._snack("No graph selected!")
            return

        path = Path(self._state.dir) / "graphs" / (selected.id + ".toml")
        includes = ", ".join(f'"{t.name}"' for t in selected.tables)
        header = f"include_tables = [{includes}]"

        try:
            content = path.read_text()
            end_first_line = content.find("\n")
            content = header + (content[end_first_line:] if end_first_line != -1 else "")
            path.write_text(content)
            app_state.open_file(str(path))
        except Exception as exc:
            self._snack(f"Could not open graph file: {exc}")

    def _rename(self):
        selected = self._state.selected_graph.get()
        if not selected:
            self._snack("No graph selected!")
            return

        RenameGraph(self._page, selected)

    def _snack(self, msg: str):
        self._page.overlay.append(ft.SnackBar(ft.Text(msg), open=True))
        self._page.update()
