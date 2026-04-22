import asyncio
from pathlib import Path
from tkinter import filedialog

from nicegui import ui

from gui import app_state


class Toolbar:
    __state: app_state.AppState

    def __init__(self, state: app_state.AppState):
        self.__state = state

        with ui.header(elevated=True).classes("items-center justify-between px-4 bg-slate-800"):
            ui.label("MyApp").classes("text-white font-bold text-lg")

            with ui.row().classes("gap-1"):
                with ui.button("File", icon="folder_open").classes("text-white").props("flat"):
                    with ui.menu():
                        ui.menu_item("New", self.__new)
                        ui.menu_item("Open", self.__load)
                        ui.menu_item("Save", self.__save)
                        ui.menu_item("Save As", self.__save_as)
                        ui.separator()
                        ui.menu_item("Exit", lambda: self.__menu_action("Exit"))

                with ui.button("Edit", icon="edit").classes("text-white").props("flat"):
                    with ui.menu():
                        ui.menu_item("Undo", lambda: self.__menu_action("Undo"))
                        ui.menu_item("Redo", lambda: self.__menu_action("Redo"))
                        ui.separator()
                        ui.menu_item("Cut", lambda: self.__menu_action("Cut"))
                        ui.menu_item("Copy", lambda: self.__menu_action("Copy"))
                        ui.menu_item("Paste", lambda: self.__menu_action("Paste"))

                with ui.button("About", icon="info").classes("text-white").props("flat"):
                    with ui.menu():
                        ui.menu_item("Documentation", lambda: self.__menu_action("Documentation"))
                        ui.menu_item("About MyApp", lambda: self.__menu_action("About MyApp"))

    def __menu_action(self, label: str):
        ui.notify(f'"{label}" clicked', position="top")

    async def __new(self):
        path = await self.__prepare_for_save()
        if not path:
            return

        self.__state.reset(str(path))
        await self.__save()

    async def __prepare_for_save(self):
        while True:
            path_name = await asyncio.to_thread(filedialog.askdirectory, title="Select Directory to Save Project")

            if not path_name:
                return

            path = Path(path_name)

            if any(path.iterdir()):
                # messagebox.showerror("Error", "Selected directory is not empty! Please select an empty directory.")
                ui.notify("Selected directory is not empty! Please select an empty directory.", position="top", color="red")
                # TODO: better
            else:
                break

        # create necessary subdirectories
        for subdir in ["graphs", "tables", "output"]:
            (path / subdir).mkdir()

        self.__state.dir = str(path)

        return path

    async def __save_as(self):
        path = await self.__prepare_for_save()
        if path:
            self.__state.save()

    async def __save(self):
        if self.__state.dir is None:
            await self.__save_as()
        else:
            self.__state.save()

    async def __load(self):
        path = await asyncio.to_thread(filedialog.askdirectory, title="Select Directory of Existing Project")

        if path:
            self.__state.load(path)
