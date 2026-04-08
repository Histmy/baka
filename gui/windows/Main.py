import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as messagebox
import tomli_w
from pathlib import Path

from graph_generator.main import make_split
from gui.AppState import AppState, Graph
from gui.components.ListBox import ListBox
from gui.control import fill_template, generate_shared_config
from gui.windows.Graph import GraphWindow


class Main(tk.Tk):
    appState: AppState
    graphs: ListBox

    def __init__(self):
        super().__init__()
        self.title("Main Window")
        self.geometry("640x480")
        self.appState = AppState([], [], [], None, "graftest")

        tk.Button(self, text="Template", command=self.pick_template).pack(pady=10)

        tk.Label(self, text="Graphs:").pack(pady=20)
        tk.Button(self, text="Add Graph", command=self.add_graph).pack()

        self.graphs = ListBox(self)
        self.graphs.pack(pady=10)

        self.graphs.register_on_single_click(self.on_selected)
        self.graphs.register_on_double_click(self.on_double_click)

        tk.Button(self, text="Process", command=self.process).pack(pady=10)

        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.quit)
        file_menu.add_command(label="Save", command=self.save)
        file_menu.add_command(label="Load", command=self.load)
        menubar.add_cascade(label="File", menu=file_menu)

    def redraw_graphs(self):
        self.graphs.redraw([graph.name for graph in self.appState.graphs])

    def save(self):
        self.appState.save(self.appState.dir)

    def load(self):
        self.appState.load(self.appState.dir)
        self.redraw_graphs()

    def process(self):
        template = self.appState.template

        if not template:
            messagebox.showerror("Error", "No template selected!")
            return

        output = fd.asksaveasfilename(defaultextension=".docx", filetypes=[("Word Documents", "*.docx")], initialdir=self.appState.dir)

        if not output:
            return

        conf = generate_shared_config(self.appState)

        conf_path = Path(self.appState.dir) / "shared_config.toml"
        with open(conf_path, "wb") as f:
            tomli_w.dump(conf, f)

        output_base = Path(self.appState.dir) / "output"

        # TODO: remove when project creation exists
        output_base.mkdir(exist_ok=True)

        for graph in self.appState.graphs:
            graph_path = Path(self.appState.dir) / "graphs" / (graph.name + ".toml")

            make_split(str(conf_path), str(graph_path), output_base / (graph.name + ".png"))

        fill_template(template, output, output_base)
        messagebox.showinfo("Success", "Document generated successfully!")

    def pick_template(self):
        path = fd.askopenfilename(filetypes=[("Word Documents", "*.docx")], initialdir=self.appState.dir)

        if path:
            self.appState.template = path

    def on_selected(self, selection: tuple[int]):
        pass

    def on_double_click(self, index: int):
        graph = self.appState.graphs[index]
        self.spawn_graph_window(graph)

    def spawn_graph_window(self, graph: Graph):
        window = GraphWindow(self, self.appState, graph)
        self.wait_window(window)
        self.redraw_graphs()

    def add_graph(self):
        graph = Graph(name="New Graph", tables=[])
        self.appState.graphs.append(graph)

        self.spawn_graph_window(graph)

        print("hotovo")
