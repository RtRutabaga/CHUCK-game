"""CHUCK — entry point.

Run the game with:

    python main.py

This file should stay tiny forever. All real logic lives in src/.
"""

import sys
from pathlib import Path

from src.core.game import Game


def crash_log_path() -> Path:
    """Return a useful writable crash-log location in source or frozen builds."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().with_name("crash_log.txt")
    return Path(__file__).resolve().parent / "crash_log.txt"


def main() -> None:
    """Create the Game and hand control to its main loop.

    Any crash is written to crash_log.txt beside the game before the
    window closes, so "it just stopped working" always has a paper
    trail (double-clicked windows close too fast to read tracebacks).
    """
    try:
        game = Game()
        game.run()
    except Exception:
        import traceback
        log = crash_log_path()
        log.write_text(traceback.format_exc(), encoding="utf-8")
        print(f"CHUCK crashed. Details written to {log}")
        raise


if __name__ == "__main__":
    main()
