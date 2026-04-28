import flet as ft

from gui.app_state import AppState
from gui.components import right_side
from gui.components.left_side import LeftSide
from gui.components.toolbar import Toolbar


def build(page: ft.Page, state: AppState) -> ft.Row:
    toolbar = Toolbar(page, state)
    page.appbar = toolbar.build()

    # ── Layout: left drawer + right content ──────────────────────────────────
    left = LeftSide(page, state)
    right = right_side.build(page, state)

    return ft.Row(
        [
            left.build(),
            ft.VerticalDivider(width=1),
            right,
        ],
        expand=True,
        spacing=0,
    )
