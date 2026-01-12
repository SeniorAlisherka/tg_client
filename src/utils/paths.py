import sys
from pathlib import Path


def app_root_dir() -> Path:
    """
    Returns project root in dev
    Returns .app bundle resource root in production
    """
    if getattr(sys, "frozen", False):
        # PyInstaller mode
        return Path(sys._MEIPASS)
    else:
        # Dev mode
        return Path(__file__).resolve().parents[2]


def app_support_dir(app_name: str) -> Path:
    base = Path.home() / "Library" / "Application Support"
    path = base / app_name
    path.mkdir(parents=True, exist_ok=True)
    return path
