import flet as ft

import gui.windows.main as main_window
from gui.app_state import AppState
from gui.windows.welcome import WelcomeWindow


def main(page: ft.Page):
    page.title = "MyApp"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 1100
    page.window.height = 720
    page.window.min_width = 800
    page.window.min_height = 500
    page.padding = 0

    welcome = WelcomeWindow(page, lambda appstate, page=page: load_main_window(page, appstate))
    page.add(welcome.build())

    page.update()


def load_main_window(page: ft.Page, appstate: AppState):
    page.controls.clear()
    page.add(main_window.build(page, appstate))
    page.update()


if __name__ == "__main__":
    ft.run(main)
