import tomllib
from pathlib import Path

import flet as ft
import tomli_w
from graph_generator.main import make_split
from word_replace.main import replace_placeholder_with_figure
import docx

from gui import app_state


class BottomPanel:
    """Template selection and document processing panel."""

    def __init__(self, page: ft.Page, state: app_state.AppState):
        self._page = page
        self._state = state

        self._template_label = ft.Text(
            "No template selected",
            size=12,
            color=ft.Colors.GREY_600,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

    # ── public widget ─────────────────────────────────────────────────────────

    def build(self) -> ft.Container:
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=24, vertical=8),
            content=ft.Column(
                [
                    ft.Divider(),
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "Select Template…",
                                icon=ft.Icons.DESCRIPTION,
                                on_click=self._select_template,
                            ),
                            self._template_label,
                        ],
                        spacing=10,
                    ),
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

    async def _select_template(self, _e):
        files = await ft.FilePicker().pick_files(
            dialog_title="Select Template",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["docx"],
        )

        if files:
            path = files[0].path
            self._state.template = path
            self._template_label.value = path or ""
            self._page.update()

    # ── process ───────────────────────────────────────────────────────────────

    async def _process(self, _e):
        if not self._state.template:
            self._snack("No template selected!", error=True)
            return
        file = await ft.FilePicker().save_file(
            dialog_title="Save Processed File",
            file_name="output.docx",
            allowed_extensions=["docx"],
        )

        if not file:
            return

        template = self._state.template

        try:
            conf = self._generate_shared_config()
            conf_path = Path(self._state.dir) / "shared_config.toml"
            with open(conf_path, "wb") as f:
                tomli_w.dump(conf, f)

            output_base = Path(self._state.dir) / "output"

            for graph in self._state.graphs:
                graph_path = Path(self._state.dir) / "graphs" / (graph.id + ".toml")
                make_split(str(conf_path), str(graph_path), output_base / (graph.name + ".png"))

            doc = docx.Document(template)
            replace_placeholder_with_figure(doc, output_base, "Figure", "Figure", "This is a sample figure.")
            doc.save(file)

            self._snack(f"Saved to {file}")
        except Exception as exc:
            self._snack(f"Processing failed: {exc}", error=True)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _generate_shared_config(self) -> dict:
        tables: dict = {}
        filters: dict = {}
        workbooks = {wb.name: {"path": wb.path} for wb in self._state.workbooks}

        for table in self._state.tables:
            with open(Path(self._state.dir) / "tables" / (table.id + ".toml"), "rb") as f:
                content = tomllib.load(f)
            tables[table.name] = content["table"]
            tables[table.name]["workbook"] = table.workbook.name if table.workbook else ""
            filters[table.name] = content["filters"]

        return {"workbooks": workbooks, "tables": tables, "filters": filters}

    def _snack(self, msg: str, *, error: bool = False):
        self._page.overlay.append(ft.SnackBar(
            ft.Text(msg),
            bgcolor=ft.Colors.RED_700 if error else None,
            open=True,
        ))
        self._page.update()
