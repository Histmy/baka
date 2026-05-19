import sys
from pathlib import Path


def resource_path(relative_path: Path) -> Path:
    meipass = getattr(sys, "_MEIPASS", None)

    if meipass is not None:
        # We are running in a PyInstaller bundle
        base_path = Path(meipass)
    else:
        # We are running in a normal Python environment
        base_path = Path.cwd()

    return base_path / relative_path
