from nicegui import ui

from gui.components import bottom_banel
from gui.components.top_panel import TopPanel
from gui.app_state import AppState


def build(state: AppState):
    with ui.column().classes("p-8 w-full h-full gap-6"):
        TopPanel(state)

        # TODO: make be at the bottom of the page

        bottom_banel.build()
