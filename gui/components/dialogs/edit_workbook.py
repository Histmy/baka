import flet as ft

from gui.app_state import Workbook


class EditWorkbookDialog:
    """Modal dialog for editing a Workbook's name and Excel source path."""

    def __init__(self, page: ft.Page, workbook: Workbook, on_saved=None):
        self._page = page
        self._workbook = workbook
        self._on_saved = on_saved

        self._name_field = ft.TextField(
            label="Name",
            value=workbook.name,
            autofocus=True,
            expand=False,
        )
        self._path_label = ft.Text(
            workbook.path or "No file selected",
            size=12,
            color=ft.Colors.GREY_600,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

        self._dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Workbook"),
            content=ft.Column(
                [
                    self._name_field,
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.INSERT_DRIVE_FILE, color=ft.Colors.BLUE_GREY_400, size=16),
                            self._path_label,
                        ],
                        spacing=6,
                    ),
                    ft.ElevatedButton(
                        "Change Source…",
                        icon=ft.Icons.FOLDER_OPEN,
                        on_click=self._pick_file,
                    ),
                ],
                tight=True,
                spacing=12,
                width=380,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=self._cancel),
                ft.ElevatedButton("Save", on_click=self._save),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.show_dialog(self._dialog)

    # ── file picker ──────────────────────────────────────────────────────────

    async def _pick_file(self):
        files = await ft.FilePicker().pick_files(
            dialog_title="Select Workbook Source",
            allowed_extensions=["xlsx", "xls"],
            allow_multiple=False,
        )

        if len(files) == 0:
            return

        path = files[0].path or ""
        self._workbook.path = path
        self._path_label.value = path
        self._page.update()

    # ── actions ──────────────────────────────────────────────────────────────

    def _save(self):
        new_name = self._name_field.value.strip()
        if new_name:
            self._workbook.name = new_name
        self._close()
        if self._on_saved:
            self._on_saved()

    def _cancel(self):
        self._close()

    def _close(self):
        self._dialog.open = False
        self._page.update()
