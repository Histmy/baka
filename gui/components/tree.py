from collections.abc import Callable

import flet as ft

from gui import app_state


class Tree(ft.Column):
    def __init__(
        self,
        page: ft.Page,
        state: app_state.AppState,
        select_workbook: Callable[[str], None],
        select_table: Callable[[str], None],
        add_table: Callable[[str], None],
    ):
        super().__init__(scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)

        self._state = state
        self._page = page
        self._select_workbook = select_workbook
        self._select_table = select_table
        self._add_table = add_table

    def rebuild(self, selected_id: str | None):
        self.controls.clear()

        selected_graph = self._state.selected_graph.get()
        ticked_ids = set(t.id for t in selected_graph.tables) if selected_graph else set()

        for workbook in self._state.workbooks:
            children_widgets = []
            for table in self._state.tables:
                if table.workbook and table.workbook.id == workbook.id:
                    is_ticked = table.id in ticked_ids
                    children_widgets.append(self._table_row(table, is_ticked, selected_id))

            self.controls.append(self._workbook_row(workbook, children_widgets, selected_id))

        self._page.update()

    def _workbook_row(self, workbook: app_state.Workbook, children: list, selected_id: str | None) -> ft.Column:
        header = ft.GestureDetector(
            on_tap=lambda _, wb=workbook: self._select_workbook(wb.id),
            content=ft.Container(
                padding=ft.padding.symmetric(vertical=4, horizontal=8),
                bgcolor=ft.Colors.BLUE_200 if selected_id == workbook.id else None,
                border_radius=4,
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.TABLE_VIEW, size=16, color=ft.Colors.BLUE_GREY_600),
                        ft.Text(workbook.name, weight=ft.FontWeight.W_500, size=13),
                        ft.IconButton(
                            icon=ft.Icons.ADD,
                            tooltip="Add table",
                            icon_color=ft.Colors.BLUE_GREY_400,
                            on_click=lambda: self._add_table(workbook.id),
                        ),
                    ],
                    spacing=6,
                ),
            ),
        )

        return ft.Column(
            [header, ft.Column(children, spacing=0)],
            spacing=0,
        )

    def _table_row(self, table: app_state.Table, ticked: bool, selected_id: str | None) -> ft.GestureDetector:
        checkbox = ft.Checkbox(
            value=ticked,
            on_change=lambda e, t=table: self._on_tick(t, e.control.value or False),
        )

        row = ft.GestureDetector(
            on_tap=lambda _, t=table: self._select_table(t.id),
            content=ft.Container(
                padding=ft.padding.only(left=24, top=2, bottom=2, right=8),
                bgcolor=ft.Colors.BLUE_200 if selected_id == table.id else None,
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

    def _on_tick(self, table: app_state.Table, checked: bool):
        selected_graph = self._state.selected_graph.get()
        if not selected_graph:
            return
        if checked and table not in selected_graph.tables:
            selected_graph.tables.append(table)
        elif not checked and table in selected_graph.tables:
            selected_graph.tables.remove(table)
