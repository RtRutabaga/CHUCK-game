"""Player settings: music and sound levels, and fullscreen.

These are the only thing the game keeps on the machine. The save is a
code the player holds, and the save file went with CONTINUE -- but a
player who turned the music down should not have it come back up
because they started over, so settings persist on their own.

Anything unreadable or out of range falls back to the defaults rather
than stopping the game from starting.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path

SETTINGS_FILENAME = "settings.json"


def default_settings_path() -> Path:
    """The per-user settings path, without depending on the working folder.

    This used to be derived from the save file's location. The save file
    is gone, so it stands on its own -- in the same place, so a player
    who already had settings keeps them.
    """
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
    return base / "CHUCK" / SETTINGS_FILENAME

# The volume sliders run 0..LEVELS in whole steps. DEFAULT_LEVEL is where
# the game's authored mix sits, so a fresh install sounds exactly as it
# was mixed and there is headroom above it.
LEVELS = 10
DEFAULT_LEVEL = 8


@dataclass
class Settings:
    music: int = DEFAULT_LEVEL
    sound: int = DEFAULT_LEVEL
    fullscreen: bool = False

    def to_json(self) -> dict:
        return {"music": self.music, "sound": self.sound,
                "fullscreen": self.fullscreen}


def _level(value, default: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        return default
    return max(0, min(LEVELS, value))


class SettingsStore:
    """Reads and writes settings.json; never raises on bad storage."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self) -> Settings:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeError):
            return Settings()
        if not isinstance(raw, dict):
            return Settings()
        fullscreen = raw.get("fullscreen", False)
        return Settings(
            music=_level(raw.get("music"), DEFAULT_LEVEL),
            sound=_level(raw.get("sound"), DEFAULT_LEVEL),
            fullscreen=fullscreen if isinstance(fullscreen, bool) else False,
        )

    def write(self, settings: Settings) -> bool:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(settings.to_json(), indent=2, sort_keys=True)
                + "\n", encoding="utf-8")
        except OSError:
            return False
        return True
