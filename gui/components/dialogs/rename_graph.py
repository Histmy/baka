from typing import Callable

import flet as ft

from gui.app_state import Graph


class RenameGraph:
    """Modal dialog for renaming a graph."""

    def __init__(self, page: ft.Page, graph: Graph, redraw_callback: Callable[[str], None]):
        self._page = page
        self._graph = graph
        self._redraw_callback = redraw_callback

        self._name_field = ft.TextField(
            label="Name",
            value=graph.name,
            autofocus=True,
            expand=False,
        )

        self._dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Rename Graph"),
            content=ft.Column(
                [self._name_field],
                tight=True,
                spacing=12,
                width=340,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=self._cancel),
                ft.ElevatedButton("Save", on_click=self._save),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.show_dialog(self._dialog)

    # ── actions ──────────────────────────────────────────────────────────────

    def _save(self):
        new_name = self._name_field.value.strip()
        if new_name:
            self._graph.name = new_name
        self._close()

    def _cancel(self):
        self._close()

    def _close(self):
        self._dialog.open = False

        self._page.update()
        self._redraw_callback(self._graph.name)
