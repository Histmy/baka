import flet as ft

from gui.app_state import AppState
from gui.components import right_side
from gui.components.left_side import LeftSide
from gui.components.toolbar import Toolbar


class MainWindow:
    """Main application window with left navigation and right content areas."""

    def __init__(self, page: ft.Page, state: AppState):
        self._page = page
        self._state = state
        self._dialog = ft.AlertDialog(
            title=ft.Text("Unsaved Changes"),
            content=ft.Text("You have unsaved changes. Are you sure you want to close?"),
            actions=[
                ft.TextButton("Cancel", on_click=self._close_dialog),
                ft.TextButton("Close without saving", on_click=self._close_window),
            ],
        )

    async def _on_close(self, e: ft.WindowEvent):
        if e.type != ft.WindowEventType.CLOSE:
            return

        if not self._state.dirty:
            await self._close_window()
            return

        self._page.show_dialog(self._dialog)

    def _close_dialog(self):
        self._dialog.open = False
        self._page.update()

    async def _close_window(self):
        self._page.window.prevent_close = False
        await self._page.window.destroy()

    def build(self) -> ft.Row:
        toolbar = Toolbar(self._page, self._state)
        self._page.appbar = toolbar.build()

        # ── Layout: left drawer + right content ──────────────────────────────────
        left = LeftSide(self._page, self._state)
        right = right_side.build(self._page, self._state)

        self._page.window.prevent_close = True
        self._page.window.on_event = self._on_close

        return ft.Row(
            [
                left.build(),
                ft.VerticalDivider(width=1),
                right,
            ],
            expand=True,
            spacing=0,
        )
