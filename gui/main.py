import flet as ft

from gui.app_state import AppState, ObservableList
from gui.components import right_side
from gui.components.left_side import LeftSide
from gui.components.toolbar import Toolbar


def build_state() -> AppState:
    return AppState(
        workbooks=ObservableList([]),
        tables=ObservableList([]),
        graphs=ObservableList([]),
        template=None,
        dir="/hopefully/does/not/exist",
    )


def main(page: ft.Page):
    page.title = "MyApp"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 1100
    page.window.height = 720
    page.window.min_width = 800
    page.window.min_height = 500
    page.padding = 0

    state = build_state()

    # ── Toolbar (AppBar) ─────────────────────────────────────────────────────
    toolbar = Toolbar(page, state)
    page.appbar = toolbar.build()

    # ── Layout: left drawer + right content ──────────────────────────────────
    left = LeftSide(page, state)
    right = right_side.build(page, state)

    page.add(
        ft.Row(
            [
                left.build(),
                ft.VerticalDivider(width=1),
                right,
            ],
            expand=True,
            spacing=0,
        )
    )

    page.update()


if __name__ == "__main__":
    ft.run(main)
