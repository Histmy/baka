from pathlib import Path

import flet as ft

from gui import app_state


class Toolbar:
    """Top app-bar with File / Edit / About menus.

    All file-picking is done via Flet's native FilePicker / DirectoryPicker —
    no tkinter import anywhere.
    """
    _page: ft.Page
    _state: app_state.AppState

    def __init__(self, page: ft.Page, state: app_state.AppState):
        self._page = page
        self._state = state

    # ── public control ────────────────────────────────────────────────────────

    def build(self) -> ft.AppBar:
        return ft.AppBar(
            title=ft.Text("MyApp", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.BLUE_GREY_900,
            actions=[
                ft.PopupMenuButton(
                    content=ft.Row(
                        [ft.Icon(ft.Icons.FOLDER_OPEN, color=ft.Colors.WHITE), ft.Text("File", color=ft.Colors.WHITE)],
                        spacing=4,
                    ),
                    items=[
                        ft.PopupMenuItem(content="New", on_click=self._new),
                        ft.PopupMenuItem(content="Open", on_click=self._load),
                        ft.PopupMenuItem(content="Save", on_click=self._save),
                        ft.PopupMenuItem(content="Save As", on_click=self._save_as),
                        ft.PopupMenuItem(),  # divider
                        ft.PopupMenuItem(content="Exit", on_click=lambda _: self._page.window.close()),
                    ],
                ),
            ],
            actions_padding=20,
        )

    # ── helpers ───────────────────────────────────────────────────────────────

    def _error(self, msg: str):
        self._page.overlay.append(ft.SnackBar(
            ft.Text(msg),
            bgcolor=ft.Colors.RED_700,
            open=True,
        ))
        self._page.update()

    def _notify(self, msg: str):
        self._page.overlay.append(ft.SnackBar(
            ft.Text(msg),
            open=True,
        ))
        self._page.update()

    # ── menu actions ──────────────────────────────────────────────────────────

    async def _new(self):
        path = await ft.FilePicker().get_directory_path(dialog_title="Select Empty Directory for New Project")

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

        self._state.dir = str(path)

        self._state.reset(str(path))
        try:
            self._state.save()
            self._notify("New project created")
        except Exception as exc:
            self._error(str(exc))

    async def _save_as(self):
        path = await ft.FilePicker().get_directory_path(dialog_title="Select Directory to Save Project")

        if not path:
            return

        try:
            self._state.save()
            self._notify("Project saved")
        except Exception as exc:
            self._error(str(exc))

    async def _save(self):
        if not self._state.dir or not Path(self._state.dir).exists():
            await self._save_as()
        else:
            try:
                self._state.save()
                self._notify("Project saved")
            except Exception as exc:
                self._error(str(exc))

    async def _load(self):
        path = await ft.FilePicker().get_directory_path(dialog_title="Select Directory of Existing Project")

        if not path:
            return

        try:
            self._state.load(path)
            self._notify("Project loaded")
        except Exception as exc:
            self._error(f"Failed to load project: {exc}")
