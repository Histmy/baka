from nicegui import ui

from gui.app_state import AppState
from gui.components.bottom_banel import BottomPanel
from gui.components.top_panel import TopPanel


def build(state: AppState):
    with ui.column().classes("p-8 w-full h-full gap-6"):
        TopPanel(state)

        # TODO: make be at the bottom of the page

        BottomPanel(state)
