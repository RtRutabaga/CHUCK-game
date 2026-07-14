"""CHUCK — entry point.

Run the game with:

    python main.py

This file should stay tiny forever. All real logic lives in src/.
"""

from src.core.game import Game


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
        from pathlib import Path

        log = Path(__file__).resolve().parent / "crash_log.txt"
        log.write_text(traceback.format_exc(), encoding="utf-8")
        print(f"CHUCK crashed. Details written to {log}")
        raise


if __name__ == "__main__":
    main()
