from pathlib import Path

def get_project_root() -> Path:
    """Returns project root folder."""
    return str(Path(__file__).parent.parent)