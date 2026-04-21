from nicegui import ui

tree_data = {
    "root": {
        "label": "Root",
        "children": {
            "child1": {"label": "Child 1", "children": {}},
            "child2": {"label": "Child 2", "children": {}},
        },
    },
    "another": {
        "label": "Root2",
        "children": {
            "child1": {"label": "Child 1", "children": {}},
            "child2": {"label": "Child 2", "children": {}},
        },
    },
}

node_counter = {"n": 3}


def render_tree():
    tree_container.clear()
    with tree_container:
        for node_id, node in tree_data.items():
            render_node(node_id, node, depth=0)


def render_node(node_id: str, node: dict, depth: int):
    indent = depth * 24

    with ui.row().style(f"align-items: center; margin-left: {indent}px; gap: 6px; margin-bottom: 4px;"):
        ui.icon("folder" if node["children"] else "article").style("font-size: 18px; color: #888;")
        ui.label(node["label"])

        if depth < 2:  # only root and depth-0 nodes can have children (2 layers deep)

            def add_child(nid=node_id, nd=node):
                node_counter["n"] += 1
                key = f"child{node_counter['n']}"
                nd["children"][key] = {"label": f"Child {node_counter['n']}", "children": {}}
                render_tree()

            ui.button("+", on_click=add_child).props("flat dense round").style("font-size: 12px; width: 22px; height: 22px; min-height: unset; color: #666;")

    if node["children"]:
        with ui.column().style(f"margin-left: {indent + 24}px; border-left: 1px solid #ddd; padding-left: 8px; gap: 0;"):
            for child_id, child_node in node["children"].items():
                render_node(child_id, child_node, depth + 1)


with ui.card().style("min-width: 320px; padding: 16px;"):
    ui.label("My Tree").style("font-weight: 500; margin-bottom: 8px;")
    tree_container = ui.column()
    render_tree()

ui.run()
