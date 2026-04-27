import flet as ft

from gui.app_state import AppState
from gui.components.template_and_process import TemplateAndProcess
from gui.components.graph_select import GraphSelect


def build(page: ft.Page, state: AppState) -> ft.Column:
    """Assemble the right-hand content area (top control panel + bottom process panel)."""
    top = TemplateAndProcess(page, state)
    bottom = GraphSelect(page, state)

    return ft.Column(
        [
            top.build(),
            bottom.build(),
        ],
        expand=True,
        spacing=0,
    )
