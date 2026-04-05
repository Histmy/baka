import tkinter as tk
from typing import Callable


class ListBox(tk.Listbox):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, exportselection=False, **kwargs)

    def redraw(self, items: list[str]):
        self.delete(0, tk.END)
        for item in items:
            self.insert(tk.END, item)

    def __handle_callback(self, event: tk.Event, callback: Callable[[tuple[int]], None]):
        widget = event.widget
        if not isinstance(widget, tk.Listbox):
            return

        selection = widget.curselection()
        if selection:
            callback(selection)

    def __handle_double_click(self, event: tk.Event, callback: Callable[[int], None]):
        widget = event.widget

        if not isinstance(widget, tk.Listbox):
            return

        callback(widget.nearest(event.y))

    def register_on_single_click(self, callback: Callable[[tuple[int]], None]):
        self.bind("<<ListboxSelect>>", lambda event: self.__handle_callback(event, callback))

    def register_on_double_click(self, callback: Callable[[int], None]):
        self.bind("<Double-1>", lambda event: self.__handle_double_click(event, callback))
