from nicegui import ui


def build():
    with ui.column().classes("p-8 w-full gap-6"):
        ui.button("Template")

        ui.button("Process")
