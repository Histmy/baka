import tkinter as tk
from tkinter import filedialog

from gui.AppState import Workbook
from gui.components.Window import Window


class WorkbookWindow(Window):
    workbook: Workbook
    name_var: tk.StringVar
    path_label: tk.Label

    def __init__(self, parent, workbook: Workbook):
        super().__init__(parent, "Workbook Window")
        self.workbook = workbook

        tk.Label(self, text="Name:").pack(pady=5)
        self.name_var = tk.StringVar(value=self.workbook.name)
        name_entry = tk.Entry(self, textvariable=self.name_var, validate="focusout", validatecommand=self.change_name)
        name_entry.pack(pady=5)

        self.path_label = tk.Label(self, text=f"Path: {self.workbook.path}")
        self.path_label.pack(pady=5)

        tk.Button(self, text="Change", command=self.select_file).pack(pady=10)

        tk.Button(self, text="Save", command=self.close).pack(pady=10)

    def change_name(self):
        # TODO: check for duplicates
        name = self.name_var.get()
        self.workbook.name = name
        return True

    def select_file(self):
        file_path = filedialog.askopenfilename(parent=self)
        if file_path:
            self.workbook.path = file_path
            self.path_label.config(text=f"Path: {self.workbook.path}")

    def close(self):
        self.change_name()
        self.destroy()
