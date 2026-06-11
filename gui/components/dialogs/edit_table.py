from typing import Callable

import flet as ft

from gui.app_state import Table


class EditTableDialog:
    """Modal dialog for renaming a Table and opening it in the system editor."""

    def __init__(self, page: ft.Page, tables: list[Table], table: Table, open_callback: Callable[[str], None], on_saved: Callable[[], None]):
        self._page = page
        self._tables = tables
        self._table = table
        self._open_callback = open_callback
        self._on_saved = on_saved

        self._name_field = ft.TextField(
            label="Name",
            value=table.name,
            autofocus=True,
            expand=False,
        )

        self._dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Table"),
            content=ft.Column(
                [
                    self._name_field,
                    ft.ElevatedButton(
                        "Open in Editor",
                        icon=ft.Icons.EDIT,
                        on_click=self._open_editor,
                    ),
                ],
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

    def _open_editor(self):
        self._open_callback(self._table.id)

    def _save(self):
        new_name = self._name_field.value.strip()
        for table in self._tables:
            if table.name == new_name and table.id != self._table.id:
                overlay = ft.AlertDialog(
                    title=ft.Text("Error"),
                    content=ft.Text("A table with this name already exists. Please choose a different name."),
                    actions=[ft.TextButton("OK", on_click=lambda _: setattr(overlay, "open", False) and self._page.update())],
                )
                self._page.overlay.append(overlay)
                overlay.open = True
                self._page.update()
                return
        self._table.name = new_name
        self._close()
        self._on_saved()

    def _cancel(self):
        self._close()

    def _close(self):
        self._dialog.open = False
        self._page.update()
