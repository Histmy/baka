import tkinter as tk

from gui.AppState import AppState, Table, Workbook
from gui.components.ListBox import ListBox
from gui.components.Window import Window
from gui.windows.Workbook import WorkbookWindow


class TableWindow(Window):
    appState: AppState
    workbooks: ListBox
    table: Table

    def __init__(self, parent, appState: AppState, table: Table):
        super().__init__(parent, "Table edit")
        self.appState = appState
        self.table = table

        tk.Label(self, text="Name:").pack(pady=(5, 0))

        self.name_var = tk.StringVar(value=self.table.name)
        name_entry = tk.Entry(self, textvariable=self.name_var, validate="focusout", validatecommand=self.change_name)
        name_entry.pack(pady=5)

        tk.Label(self, text="Workbooks:").pack(pady=(5, 0))

        tk.Button(self, text="Add Workbook", command=self.add_workbook).pack(pady=10)

        self.workbooks = ListBox(self)
        self.workbooks.pack(pady=10)
        self.redraw_workbooks()

        self.workbooks.register_on_double_click(self.on_selected)
        self.workbooks.register_on_single_click(self.select_workbook)

        tk.Button(self, text="Edit", command=self.edit).pack(pady=10)

        tk.Button(self, text="Close", command=self.close).pack(pady=10)

    def change_name(self):
        self.table.name = self.name_var.get()
        return True

    def select_workbook(self, selection: tuple[int]):
        index = selection[0]
        workbook = self.appState.workbooks[index]
        self.table.workbook = workbook

    def close(self):
        self.change_name()
        self.destroy()

    def insert_workbook(self, workbook: Workbook):
        self.appState.workbooks.append(workbook)
        self.workbooks.insert(tk.END, workbook.name)

    def add_workbook(self):
        workbook = Workbook(name="New Workbook", path=None)
        # Create the secondary window, passing the main window as its parent
        self.spawn_window(WorkbookWindow, workbook)

        self.insert_workbook(workbook)

    def redraw_workbooks(self):
        self.workbooks.redraw([workbook.name for workbook in self.appState.workbooks])

        if self.table.workbook is not None:
            index = self.appState.workbooks.index(self.table.workbook)
            self.workbooks.selection_set(index)

    def on_selected(self, index: int):
        workbook = self.appState.workbooks[index]
        self.spawn_window(WorkbookWindow, workbook)
        self.redraw_workbooks()

    def edit(self): ...
