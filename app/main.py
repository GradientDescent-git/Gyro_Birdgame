from __future__ import annotations

import runpy
import sys
from pathlib import Path


def main() -> None:
    """Launch the VisionBird game."""

    project_root = Path(__file__).resolve().parent.parent

    game_source = (
        project_root
        / "third_party"
        / "angry-birds-python"
        / "src"
        / "main.py"
    )

    if not game_source.exists():
        raise FileNotFoundError(
            f"VisionBird game entry point not found: {game_source}"
        )

    game_src_dir = str(game_source.parent)

    if game_src_dir not in sys.path:
        sys.path.insert(
            0,
            game_src_dir,
        )

    runpy.run_path(
        str(game_source),
        run_name="__main__",
    )


if __name__ == "__main__":
    main()
