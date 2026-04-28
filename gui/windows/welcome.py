import flet as ft

from gui.app_state import AppState
from pathlib import Path
from collections.abc import Callable


class WelcomeWindow:
    def __init__(self, page: ft.Page, on_project_loaded: Callable[[AppState], None]):
        self._page = page
        self._on_project_loaded = on_project_loaded

    def build(self) -> ft.Column:
        return ft.Column(
            [
                ft.Text("Welcome to MyApp", size=30, weight=ft.FontWeight.BOLD),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Create New Project",
                            icon=ft.Icons.CREATE_NEW_FOLDER,
                            on_click=self._create_new_project,
                        ),
                        ft.ElevatedButton(
                            "Open Existing Project",
                            icon=ft.Icons.FOLDER_OPEN,
                            on_click=self._open_existing_project,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        )

    async def _create_new_project(self):
        path = await ft.FilePicker().get_directory_path(dialog_title="Select Empty Directory")
        if not path:
            return

        path = Path(path)

        # Validate: must be empty
        if any(path.iterdir()):
            self._error("Selected directory is not empty! Please choose an empty directory.")
            return

        # Create standard subdirs
        for subdir in ["graphs", "tables", "output"]:
            (path / subdir).mkdir(exist_ok=True)

        state = AppState(str(path))

        try:
            state.save()
            self._on_project_loaded(state)
        except Exception as exc:
            self._error(str(exc))

    async def _open_existing_project(self):
        path = await ft.FilePicker().get_directory_path(dialog_title="Select Directory of Existing Project")
        if not path:
            return

        try:
            state = AppState(str(path))
            state.load(str(path))
            self._on_project_loaded(state)
        except Exception as exc:
            self._error(str(exc))

    def _error(self, msg: str):
        self._page.overlay.append(
            ft.SnackBar(
                ft.Text(msg),
                bgcolor=ft.Colors.RED_700,
                open=True,
            )
        )
        self._page.update()
