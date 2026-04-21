from nicegui import ui


def menu_action(label: str):
    ui.notify(f'"{label}" clicked', position="top")


def build():
    with ui.header(elevated=True).classes("items-center justify-between px-4 bg-slate-800"):
        ui.label("MyApp").classes("text-white font-bold text-lg")

        with ui.row().classes("gap-1"):
            with ui.button("File", icon="folder_open").classes("text-white").props("flat"):
                with ui.menu():
                    ui.menu_item("New", lambda: menu_action("New"))
                    ui.menu_item("Open", lambda: menu_action("Open"))
                    ui.menu_item("Save", lambda: menu_action("Save"))
                    ui.separator()
                    ui.menu_item("Exit", lambda: menu_action("Exit"))

            with ui.button("Edit", icon="edit").classes("text-white").props("flat"):
                with ui.menu():
                    ui.menu_item("Undo", lambda: menu_action("Undo"))
                    ui.menu_item("Redo", lambda: menu_action("Redo"))
                    ui.separator()
                    ui.menu_item("Cut", lambda: menu_action("Cut"))
                    ui.menu_item("Copy", lambda: menu_action("Copy"))
                    ui.menu_item("Paste", lambda: menu_action("Paste"))

            with ui.button("About", icon="info").classes("text-white").props("flat"):
                with ui.menu():
                    ui.menu_item("Documentation", lambda: menu_action("Documentation"))
                    ui.menu_item("About MyApp", lambda: menu_action("About MyApp"))
