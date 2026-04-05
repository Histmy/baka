import tkinter as tk

from gui.AppState import AppState, Graph
from gui.components.ListBox import ListBox
from gui.windows.Graph import GraphWindow


class Main(tk.Tk):
    appState: AppState
    graphs: ListBox

    def __init__(self):
        super().__init__()
        self.title("Main Window")
        self.geometry("640x480")
        self.appState = AppState([], [], [])

        tk.Label(self, text="Graphs:").pack(pady=20)
        tk.Button(self, text="Add Graph", command=self.add_graph).pack()

        self.graphs = ListBox(self)
        self.graphs.pack(pady=10)

        self.graphs.register_on_single_click(self.on_selected)
        self.graphs.register_on_double_click(self.on_double_click)

    def redraw_graphs(self):
        self.graphs.redraw([graph.name for graph in self.appState.graphs])

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
