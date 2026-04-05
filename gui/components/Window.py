import tkinter as tk


class Window(tk.Toplevel):
    def __init__(self, parent, title: str):
        super().__init__(parent)
        self.title(title)
        self.geometry("640x480")

    def spawn_window(self, window_class: type, *args, **kwargs):
        window = window_class(self, *args, **kwargs)
        self.wait_window(window)

    @staticmethod
    def redraw_list_box(list_box: tk.Listbox, items: list[str]):
        list_box.delete(0, tk.END)
        for item in items:
            list_box.insert(tk.END, item)
