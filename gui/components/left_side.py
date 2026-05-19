from pathlib import Path
from typing import Literal, Optional

import flet as ft

from gui import app_state
from gui.components.dialogs.edit_table import EditTableDialog
from gui.components.dialogs.edit_workbook import EditWorkbookDialog
from gui.components.tree import Tree
from gui.util.resource_path import resource_path


class LeftSide:
    """Left navigation panel: workbook/table tree with add/edit/delete controls.

    Uses Flet's FilePicker for opening Excel files — no tkinter.
    """

    def __init__(self, page: ft.Page, state: app_state.AppState):
        self._page = page
        self._state = state
        self._selected_type: Optional[Literal["workbook", "table"]] = None
        self._selected_id: Optional[str] = None
        self._ticked_table_ids: set[str] = set()

        # Native file picker for adding workbooks
        self._wb_picker = ft.FilePicker()

        # Toolbar buttons (kept as attrs so we can enable/disable them)
        self._edit_btn = ft.IconButton(
            icon=ft.Icons.EDIT,
            tooltip="Edit selected item",
            icon_color=ft.Colors.BLUE_GREY_400,
            on_click=self._edit,
            disabled=True,
        )
        self._delete_btn = ft.IconButton(
            icon=ft.Icons.DELETE,
            tooltip="Delete selected item",
            icon_color=ft.Colors.BLUE_GREY_400,
            on_click=self._delete_selected,
            disabled=True,
        )

        # Tree container — rebuilt whenever data changes
        self._tree_column = Tree(page, state, self._select_workbook, self._select_table, self._add_table)

        # Listen for data changes
        state.workbooks.register_listener(lambda _: self._rebuild_tree())
        state.tables.register_listener(lambda _: self._rebuild_tree())
        state.selected_graph.register(self._on_graph_change)

        self._rebuild_tree()

    # ── public widget ─────────────────────────────────────────────────────────

    def build(self) -> ft.Container:
        toolbar_row = ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.ADD,
                    tooltip="Add workbook",
                    icon_color=ft.Colors.BLUE_GREY_400,
                    on_click=self._add_workbook,
                ),
                ft.Container(expand=True),
                self._edit_btn,
                self._delete_btn,
            ],
            spacing=0,
        )

        return ft.Container(
            width=260,
            bgcolor=ft.Colors.BLUE_GREY_50,
            padding=ft.padding.all(8),
            content=ft.Column(
                [
                    toolbar_row,
                    ft.Divider(height=1),
                    self._tree_column,
                ],
                spacing=4,
                expand=True,
            ),
        )

    # ── selection ─────────────────────────────────────────────────────────────

    def _select_workbook(self, workbook_id: str):
        self._selected_id = workbook_id
        self._selected_type = "workbook"
        self._edit_btn.disabled = False
        self._delete_btn.disabled = False
        self._page.update()
        self._rebuild_tree()

    def _select_table(self, table_id: str):
        self._selected_id = table_id
        self._selected_type = "table"
        self._edit_btn.disabled = False
        self._delete_btn.disabled = False
        self._page.update()
        self._rebuild_tree()

    # ── tick (graph membership) ───────────────────────────────────────────────

    def _on_graph_change(self):
        self._rebuild_tree()

    def _rebuild_tree(self):
        self._tree_column.rebuild(self._selected_id)

    # ── CRUD actions ──────────────────────────────────────────────────────────

    async def _add_workbook(self):
        file = await self._wb_picker.pick_files(
            dialog_title="Select Excel Workbook",
            allowed_extensions=["xlsx", "xls"],
            allow_multiple=False,
        )

        self._on_workbook_picked(file)

    def _on_workbook_picked(self, e: list[ft.FilePickerFile]):
        if len(e) == 0:
            return
        path = e[0].path
        n = len(self._state.workbooks) + 1
        self._state.workbooks.append(app_state.Workbook.new(name=f"New Workbook {n}", path=(path or "")))
        # listener triggers _rebuild

    def _add_table(self, workbook_id: str):
        workbook = next((wb for wb in self._state.workbooks if wb.id == workbook_id), None)
        if not workbook:
            return

        n = len(self._state.tables) + 1
        table = app_state.Table.new(name=f"New Table {n}", workbook=workbook)
        self._state.tables.append(table)

        # create TOML with hints
        toml_path = Path(self._state.dir) / "tables" / (table.id + ".toml")
        template_path = resource_path(Path("gui") / "toml_templates" / "table.toml")
        toml_path.write_text(template_path.read_text())

    def _edit(self):
        if not self._selected_id:
            return
        if self._selected_type == "workbook":
            workbook = next((wb for wb in self._state.workbooks if wb.id == self._selected_id), None)
            if workbook:
                EditWorkbookDialog(self._page, workbook, on_saved=self._rebuild_tree)
        else:
            table = next((t for t in self._state.tables if t.id == self._selected_id), None)
            if table:
                EditTableDialog(self._page, table, open_callback=self._open_table, on_saved=self._rebuild_tree)

    def _open_table(self, table_id: str):
        path = Path(self._state.dir) / "tables" / (table_id + ".toml")
        app_state.open_file(str(path))

    def _delete_selected(self):
        if not self._selected_id or not self._selected_type:
            return

        if self._selected_type == "workbook":
            wb = next((wb for wb in self._state.workbooks if wb.id == self._selected_id), None)
            if wb:
                # remove orphaned tables first
                for table in [t for t in self._state.tables if t.workbook.id == self._selected_id]:
                    self._state.tables.remove(table)
                self._state.workbooks.remove(wb)
        else:
            table = next((t for t in self._state.tables if t.id == self._selected_id), None)
            if table:
                self._state.tables.remove(table)
