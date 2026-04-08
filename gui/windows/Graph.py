from pathlib import Path
import os.path
import tkinter as tk

from gui.AppState import AppState, Graph, Table
from gui.components.ListBox import ListBox
from gui.components.Window import Window
from gui.windows.Table import TableWindow


class GraphWindow(Window):
    appState: AppState
    tables: ListBox
    graph: Graph

    def __init__(self, parent, appState: AppState, graph: Graph):
        super().__init__(parent, "Graph Window")
        self.appState = appState
        self.graph = graph

        tk.Label(self, text="Name:").pack(pady=5)
        self.name_var = tk.StringVar(value=self.graph.name)
        name_entry = tk.Entry(self, textvariable=self.name_var, validate="focusout", validatecommand=self.change_name)
        name_entry.pack(pady=5)

        self.tables = ListBox(self, selectmode=tk.MULTIPLE)
        self.tables.pack(pady=10)
        self.redraw_tables()

        self.tables.register_on_single_click(self.on_selected)
        self.tables.register_on_double_click(self.on_double_click)

        tk.Button(self, text="Add Table", command=self.add_table).pack(pady=10)

        tk.Button(self, text="Edit", command=self.edit).pack(pady=10)

        tk.Button(self, text="Close", command=self.close).pack(pady=10)

    def redraw_tables(self):
        self.tables.redraw([table.name for table in self.appState.tables])

        for table in self.graph.tables:
            index = self.appState.tables.index(table)
            self.tables.selection_set(index)

    def change_name(self):
        # rename file if it exists
        old_name = Path(self.appState.dir) / "graphs" / (self.graph.name + ".toml")
        new_name = Path(self.appState.dir) / "graphs" / (self.name_var.get() + ".toml")
        if old_name != new_name and os.path.isfile(old_name):
            os.rename(old_name, new_name)

        self.graph.name = self.name_var.get()
        return True

    def close(self):
        self.change_name()
        self.destroy()

    def edit(self):
        name = Path(self.appState.dir) / "graphs" / (self.graph.name + ".toml")

        name.parent.mkdir(parents=True, exist_ok=True)

        includes = ", ".join([f'"{table.name}"' for table in self.graph.tables])
        header = f"include_tables = [{includes}]"

        if not os.path.isfile(name):
            with open(name, "w") as f:
                f.write(header + "\n\n[graph]\n")
        else:
            with open(name, "r+") as f:
                content = f.read()
                end_first_line = content.find("\n")
                if end_first_line != -1:
                    content = header + content[end_first_line:]
                else:
                    content = header
                f.seek(0)
                f.write(content)
                f.truncate()

        self.edit_file(str(name))

    def on_selected(self, selection: tuple[int]):
        self.graph.tables.clear()

        for index in selection:
            table = self.appState.tables[index]
            self.graph.tables.append(table)

    def on_double_click(self, index: int):
        table = self.appState.tables[index]
        window = TableWindow(self, self.appState, table)
        self.wait_window(window)
        self.redraw_tables()

    def add_table(self):
        # Update the Listbox or other UI elements to reflect the new table
        table = Table(name="New Table", workbook=None, stuff="")
        # Update the Listbox with the new table
        window = TableWindow(self, self.appState, table)
        self.appState.tables.append(table)

        self.wait_window(window)

        self.redraw_tables()
