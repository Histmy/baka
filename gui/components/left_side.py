from pathlib import Path
from typing import Optional

import flet as ft

from gui import app_state
from gui.components.dialogs.edit_workbook import EditWorkbookDialog
from gui.components.dialogs.edit_table import EditTableDialog


class LeftSide:
    """Left navigation panel: workbook/table tree with add/edit/delete controls.

    Uses Flet's FilePicker for opening Excel files — no tkinter.
    """

    def __init__(self, page: ft.Page, state: app_state.AppState):
        self._page = page
        self._state = state
        self._selected_type: Optional[str] = None  # "workbook" | "table" | None
        self._selected_id: Optional[str] = None
        self._ticked_table_ids: set[str] = set()

        # Native file picker for adding workbooks
        self._wb_picker = ft.FilePicker()

        # Toolbar buttons (kept as attrs so we can enable/disable them)
        self._add_table_btn = ft.IconButton(
            icon=ft.Icons.ADD,
            tooltip="Add table to selected workbook",
            icon_color=ft.Colors.BLUE_GREY_400,
            on_click=self._add_table,
            disabled=True,
        )
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
        self._tree_column = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)

        # Listen for data changes
        state.workbooks.register_listener(lambda _: self._rebuild())
        state.tables.register_listener(lambda _: self._rebuild())
        state.selected_graph.register(self._on_graph_change)

        self._rebuild()

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
                self._add_table_btn,
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

    # ── tree building ─────────────────────────────────────────────────────────

    def _rebuild(self):
        self._tree_column.controls.clear()
        self._select_none()

        selected_graph = self._state.selected_graph.get()
        ticked_ids = set(t.id for t in selected_graph.tables) if selected_graph else set()

        for workbook in self._state.workbooks:
            children_widgets = []
            for table in self._state.tables:
                if table.workbook and table.workbook.id == workbook.id:
                    is_ticked = table.id in ticked_ids
                    children_widgets.append(
                        self._table_row(table, is_ticked)
                    )

            self._tree_column.controls.append(
                self._workbook_row(workbook, children_widgets)
            )

        self._page.update()

    def _workbook_row(self, workbook: app_state.Workbook, children: list) -> ft.Column:
        header = ft.GestureDetector(
            on_tap=lambda _, wb=workbook: self._select_workbook(wb.id),
            content=ft.Container(
                padding=ft.padding.symmetric(vertical=4, horizontal=8),
                border_radius=4,
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.TABLE_VIEW, size=16, color=ft.Colors.BLUE_GREY_600),
                        ft.Text(workbook.name, weight=ft.FontWeight.W_500, size=13),
                    ],
                    spacing=6,
                ),
            ),
        )

        return ft.Column(
            [header, ft.Column(children, spacing=0)],
            spacing=0,
        )

    def _table_row(self, table: app_state.Table, ticked: bool):
        checkbox = ft.Checkbox(
            value=ticked,
            on_change=lambda e, t=table: self._on_tick(t, e.control.value or False),
        )

        row = ft.GestureDetector(
            on_tap=lambda _, t=table: self._select_table(t.id),
            content=ft.Container(
                padding=ft.padding.only(left=24, top=2, bottom=2, right=8),
                border_radius=4,
                content=ft.Row(
                    [
                        checkbox,
                        ft.Icon(ft.Icons.TABLE_CHART, size=14, color=ft.Colors.BLUE_GREY_400),
                        ft.Text(table.name, size=12),
                    ],
                    spacing=6,
                ),
            ),
        )

        return row

    # ── selection ─────────────────────────────────────────────────────────────

    def _select_workbook(self, workbook_id: str):
        self._selected_id = workbook_id
        self._selected_type = "workbook"
        self._add_table_btn.disabled = False
        self._edit_btn.disabled = False
        self._delete_btn.disabled = False
        self._page.update()

    def _select_table(self, table_id: str):
        self._selected_id = table_id
        self._selected_type = "table"
        self._add_table_btn.disabled = True
        self._edit_btn.disabled = False
        self._delete_btn.disabled = False
        self._page.update()

    def _select_none(self):
        self._selected_id = None
        self._selected_type = None
        self._add_table_btn.disabled = True
        self._edit_btn.disabled = True
        self._delete_btn.disabled = True

    # ── tick (graph membership) ───────────────────────────────────────────────

    def _on_tick(self, table: app_state.Table, checked: bool):
        selected_graph = self._state.selected_graph.get()
        if not selected_graph:
            return
        if checked and table not in selected_graph.tables:
            selected_graph.tables.append(table)
        elif not checked and table in selected_graph.tables:
            selected_graph.tables.remove(table)

    def _on_graph_change(self, graph: Optional[app_state.Graph]):
        self._rebuild()

    # ── CRUD actions ──────────────────────────────────────────────────────────

    async def _add_workbook(self, _e):
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
        self._state.workbooks.append(
            app_state.Workbook.new(name=f"New Workbook {n}", path=(path or ""))
        )
        # listener triggers _rebuild

    def _add_table(self, _e):
        if not self._selected_id or self._selected_type != "workbook":
            return
        selected_wb_id = self._selected_id
        workbook = next((wb for wb in self._state.workbooks if wb.id == selected_wb_id), None)
        if not workbook:
            return

        n = len(self._state.tables) + 1
        table = app_state.Table.new(name=f"New Table {n}", workbook=workbook)
        self._state.tables.append(table)

        # create stub TOML
        path = Path(self._state.dir) / "tables" / (table.id + ".toml")
        path.write_text("[table]\n\n[filters]")

    def _edit(self, _e):
        if not self._selected_id:
            return
        if self._selected_type == "workbook":
            workbook = next((wb for wb in self._state.workbooks if wb.id == self._selected_id), None)
            if workbook:
                EditWorkbookDialog(self._page, workbook, on_saved=self._rebuild)
        else:
            table = next((t for t in self._state.tables if t.id == self._selected_id), None)
            if table:
                EditTableDialog(self._page, table, open_callback=self._open_table, on_saved=self._rebuild)

    def _open_table(self, table_id: str):
        path = Path(self._state.dir) / "tables" / (table_id + ".toml")
        app_state.open_file(str(path))

    def _delete_selected(self, _e):
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
