from nicegui import ui


# ── Toolbar menu actions (replace with your logic) ──────────────────────────


def menu_action(label: str):
    ui.notify(f'"{label}" clicked', position="top")


# ── Build the app ────────────────────────────────────────────────────────────

with ui.header(elevated=True).classes("items-center justify-between px-4 bg-slate-800"):
    ui.label("MyApp").classes("text-white font-bold text-lg")

    # Menu bar
    with ui.row().classes("gap-1"):
        # File menu
        with ui.button("File", icon="folder_open").classes("text-white").props("flat"):
            with ui.menu():
                ui.menu_item("New", lambda: menu_action("New"))
                ui.menu_item("Open", lambda: menu_action("Open"))
                ui.menu_item("Save", lambda: menu_action("Save"))
                ui.separator()
                ui.menu_item("Exit", lambda: menu_action("Exit"))

        # Edit menu
        with ui.button("Edit", icon="edit").classes("text-white").props("flat"):
            with ui.menu():
                ui.menu_item("Undo", lambda: menu_action("Undo"))
                ui.menu_item("Redo", lambda: menu_action("Redo"))
                ui.separator()
                ui.menu_item("Cut", lambda: menu_action("Cut"))
                ui.menu_item("Copy", lambda: menu_action("Copy"))
                ui.menu_item("Paste", lambda: menu_action("Paste"))

        # About menu
        with ui.button("About", icon="info").classes("text-white").props("flat"):
            with ui.menu():
                ui.menu_item("Documentation", lambda: menu_action("Documentation"))
                ui.menu_item("About MyApp", lambda: menu_action("About MyApp"))


# ── Left drawer – accordion navigation ──────────────────────────────────────

with ui.left_drawer(value=True, bordered=True).classes("bg-slate-50 p-2"):
    ui.label("Navigation").classes("text-xs font-semibold text-slate-400 uppercase px-2 pt-2 pb-1")

    sections = {
        "Dashboard": ["Overview", "Statistics", "Reports"],
        "Projects": ["Active", "Archived", "Templates"],
        "Users": ["All Users", "Roles", "Permissions"],
        "Settings": ["General", "Appearance", "Integrations"],
    }

    for section, items in sections.items():
        with ui.expansion(section, icon="chevron_right").classes("w-full").props("dense"):
            for item in items:
                with ui.item(on_click=lambda i=item: ui.notify(f"Opened: {i}", position="top-right")):
                    with ui.item_section():
                        ui.item_label(item).classes("text-sm text-slate-600")


# ── Main content – right panel ───────────────────────────────────────────────

with ui.column().classes("p-8 w-full gap-6"):
    ui.label("Control Panel").classes("text-2xl font-bold text-slate-700")
    ui.separator()

    # Dropdown
    with ui.column().classes("gap-1"):
        ui.label("Select an option").classes("text-sm font-medium text-slate-500")
        ui.select(
            options=["Option A", "Option B", "Option C", "Option D"],
            value="Option A",
            on_change=lambda e: ui.notify(f"Selected: {e.value}", position="top-right"),
        ).classes("w-64")

    # Buttons
    with ui.row().classes("gap-3"):
        ui.button(
            "Primary Action",
            icon="check_circle",
            on_click=lambda: ui.notify("Primary action triggered!", color="positive", position="top-right"),
        ).props("unelevated").classes("bg-slate-700 text-white")

        ui.button(
            "Secondary Action",
            icon="refresh",
            on_click=lambda: ui.notify("Secondary action triggered!", position="top-right"),
        ).props("outline").classes("text-slate-700")

    # Input field
    with ui.column().classes("gap-1"):
        ui.label("Input").classes("text-sm font-medium text-slate-500")
        with ui.row().classes("gap-2 items-center"):
            text_input = ui.input(
                placeholder="Type something...",
            ).classes("w-64")
            ui.button(
                "Submit",
                icon="send",
                on_click=lambda: ui.notify(f'Submitted: "{text_input.value}"', position="top-right"),
            ).props("unelevated").classes("bg-slate-700 text-white")


ui.run(title="MyApp", dark=False)
