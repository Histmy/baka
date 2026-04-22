import asyncio
import tomllib
from pathlib import Path
from tkinter import filedialog

import docx
import tomli_w
from nicegui import ui

from graph_generator.main import make_split
from gui import app_state
from word_replace.main import replace_placeholder_with_figure


class BottomPanel:
    __state: app_state.AppState

    def __init__(self, state: app_state.AppState):
        self.__state = state

        with ui.column().classes("p-8 w-full gap-6"):
            ui.button("Template", on_click=self.__select_template)

            ui.button("Process", on_click=self.__process)

    async def __select_template(self):
        file = await asyncio.to_thread(filedialog.askopenfilename, title="Select Template", filetypes=[("Word files", "*.docx")])
        if file:
            self.__state.template = file

    async def __process(self):
        template = self.__state.template
        if not template:
            # todo: show error message
            return

        dest = await asyncio.to_thread(
            filedialog.asksaveasfilename, title="Save Processed File", defaultextension=".docx", filetypes=[("Word files", "*.docx")]
        )
        if not dest:
            return

        conf = self.__generate_shared_config()

        conf_path = Path(self.__state.dir) / "shared_config.toml"
        with open(conf_path, "wb") as f:
            tomli_w.dump(conf, f)

        output_base = Path(self.__state.dir) / "output"

        for graph in self.__state.graphs:
            graph_path = Path(self.__state.dir) / "graphs" / (graph.id + ".toml")

            make_split(str(conf_path), str(graph_path), output_base / (graph.name + ".png"))

        self.__fill_template(template, dest, output_base)

    def __generate_shared_config(self):
        tables = {}
        filters = {}
        workbooks = {workbook.name: {"path": workbook.path} for workbook in self.__state.workbooks}

        for table in self.__state.tables:
            with open(Path(self.__state.dir) / "tables" / (table.id + ".toml"), "rb") as f:
                content = tomllib.load(f)
                tables[table.name] = content["table"]
                tables[table.name]["workbook"] = table.workbook.name if table.workbook else ""

                filters[table.name] = content["filters"]

        return {
            "workbooks": workbooks,
            "tables": tables,
            "filters": filters,
        }

    def __fill_template(self, template_path: str, output_path: str, graphs_dir: Path):
        doc = docx.Document(template_path)

        replace_placeholder_with_figure(doc, graphs_dir, "Figure", "Figure", "This is a sample figure.")

        doc.save(output_path)
