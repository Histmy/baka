import flet as ft

from gui.app_state import AppState
from gui.components.bottom_panel import BottomPanel
from gui.components.top_panel import TopPanel


def build(page: ft.Page, state: AppState) -> ft.Column:
    """Assemble the right-hand content area (top control panel + bottom process panel)."""
    top = TopPanel(page, state)
    bottom = BottomPanel(page, state)

    return ft.Column(
        [
            top.build(),
            ft.Container(expand=True),   # push bottom panel to... the bottom
            bottom.build(),
        ],
        expand=True,
        spacing=0,
    )
