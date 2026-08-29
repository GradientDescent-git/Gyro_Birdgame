from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional


class GameController:
    """
    High-level orchestrator for VisionBird game lifecycle.
    Manages initialization, game loop execution, gesture input integration,
    mouse fallback, and clean resource teardown.
    """

    def __init__(self, project_root: Optional[Path] = None) -> None:
        if project_root is None:
            self.project_root = Path(__file__).resolve().parent.parent.parent
        else:
            self.project_root = project_root

        self.game_entry = (
            self.project_root
            / "third_party"
            / "angry-birds-python"
            / "src"
            / "main.py"
        )

    def run(self) -> None:
        """Launch and run the main game loop."""
        if not self.game_entry.exists():
            raise FileNotFoundError(f"Game entry point not found: {self.game_entry}")

        game_src_dir = str(self.game_entry.parent)
        if game_src_dir not in sys.path:
            sys.path.insert(0, game_src_dir)

        import runpy

        runpy.run_path(str(self.game_entry), run_name="__main__")
