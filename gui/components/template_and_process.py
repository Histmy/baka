from pathlib import Path

import docx
import flet as ft
import tomli_w

from graph_generator.main import make_split
from gui import app_state
from gui.util.shared_config import generate_shared_config
from word_replace.main import replace_placeholder_with_figure


class TemplateAndProcess:
    """Template selection and document processing panel."""

    def __init__(self, page: ft.Page, state: app_state.AppState):
        self._page = page
        self._state = state

        self._template_label = ft.Text(
            state.template.get() or "No template selected",
            size=12,
            color=ft.Colors.GREY_600,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

        state.template.register_listener(self._change_template_label)

    def _change_template_label(self, value: str | None):
        self._template_label.value = value or "No template selected"
        self._template_label.update()

    # ── public widget ─────────────────────────────────────────────────────────

    def build(self) -> ft.Container:
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=24, vertical=16),
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "Select Template",
                                icon=ft.Icons.DESCRIPTION,
                                on_click=self._select_template,
                            ),
                            self._template_label,
                        ],
                        spacing=10,
                    ),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        "Process",
                        icon=ft.Icons.PLAY_ARROW,
                        bgcolor=ft.Colors.TEAL_700,
                        color=ft.Colors.WHITE,
                        on_click=self._process,
                    ),
                ],
                spacing=12,
            ),
        )

    # ── template picker ───────────────────────────────────────────────────────

    async def _select_template(self):
        files = await ft.FilePicker().pick_files(
            dialog_title="Select Template",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["docx"],
        )

        if files:
            path = files[0].path
            self._state.template.set(path)
            self._page.update()

    # ── process ───────────────────────────────────────────────────────────────

    async def _process(self):
        template = self._state.template.get()

        if not template:
            self._snack("No template selected!", error=True)
            return
        file = await ft.FilePicker().save_file(
            dialog_title="Save Processed File",
            file_name="output.docx",
            allowed_extensions=["docx"],
        )

        if not file:
            return

        try:
            conf = generate_shared_config(self._state)
            path = Path(self._state.dir)
            conf_path = path / "shared_config.toml"
            with open(conf_path, "wb") as f:
                tomli_w.dump(conf, f)
        except Exception as exc:
            self._dialog("Error", ft.Text(f"Failed to generate config: {exc}"))
            return

        try:
            output_base = path / "output"

            for graph in self._state.graphs:
                graph_path = path / "graphs" / (graph.id + ".toml")
                try:
                    make_split(str(conf_path), str(graph_path), output_base / (graph.name + ".png"))
                except Exception as exc:
                    self._dialog("Error", ft.Text(f'Failed to generate graph "{graph.name}": {exc}'))
                    return
        except Exception as exc:
            self._dialog("Error", ft.Text(f"Graph generation failed: {exc}"))
            return

        try:
            doc = docx.Document(template)
            replace_placeholder_with_figure(doc, output_base, "Figure", "Figure", "This is a sample figure.")
            doc.save(file)
        except Exception as exc:
            self._dialog("Error", ft.Text(f"Failed to generate document: {exc}"))
            return

        self._snack(f"Successfully saved to {file}")

    # ── helpers ───────────────────────────────────────────────────────────────

    def _snack(self, msg: str, *, error: bool = False):
        self._page.overlay.append(
            ft.SnackBar(
                ft.Text(msg),
                bgcolor=ft.Colors.RED_700 if error else None,
                open=True,
            )
        )
        self._page.update()

    def _dialog(self, title: str, content: ft.Control):
        def close():
            dialog.open = False
            self._page.update()

        dialog = ft.AlertDialog(title=ft.Text(title), content=content, actions=[ft.ElevatedButton("Close", on_click=lambda _: close())])

        self._page.overlay.append(dialog)

        dialog.open = True
        self._page.update()
