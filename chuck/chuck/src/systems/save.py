"""Small, versioned JSON saves for checkpoint restoration.

Only durable resume state belongs here. Runtime entities, scene objects, enemy
positions, animation timers, and camera state are rebuilt from authored data.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path

from src.core import config


SAVE_VERSION = 1


def default_save_path() -> Path:
    """Return the per-user save path without depending on the working folder."""
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
    return base / "CHUCK" / "save.json"


@dataclass(frozen=True)
class SaveRecord:
    checkpoint_id: str
    sanity: int
    progress_flags: tuple[str, ...]
    # The overall-game cigarette total (session 128). Defaults keep
    # pre-counter saves valid — they simply resume with zero banked.
    cigarettes: int = 0
    # Deaths this playthrough. Defaulted for the same reason: saves
    # written before the counter existed resume with none recorded.
    deaths: int = 0
    # Who Chuck has already had a first word from, as (map, x, y, line)
    # -- the second-word memory (WorldScene._second_word). Saved so a
    # reload does not have everybody introduce themselves again.
    spoken: tuple[tuple[str, int, int, str], ...] = ()

    def to_json(self) -> dict:
        return {
            "version": SAVE_VERSION,
            "checkpoint_id": self.checkpoint_id,
            "sanity": self.sanity,
            "progress_flags": list(self.progress_flags),
            "cigarettes": self.cigarettes,
            "deaths": self.deaths,
            "spoken": [list(entry) for entry in self.spoken],
        }


class SaveSystem:
    """Reads and atomically writes the single player save slot."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else default_save_path()

    def load(self) -> SaveRecord | None:
        """Return a valid current-version record, or None for any bad save."""
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeError):
            return None
        if not isinstance(raw, dict) or raw.get("version") != SAVE_VERSION:
            return None
        checkpoint_id = raw.get("checkpoint_id")
        sanity = raw.get("sanity")
        flags = raw.get("progress_flags")
        if not isinstance(checkpoint_id, str) or not checkpoint_id:
            return None
        if isinstance(sanity, bool) or not isinstance(sanity, int):
            return None
        if not 0 < sanity <= config.SANITY_MAX:
            return None
        if (
            not isinstance(flags, list)
            or not all(isinstance(flag, str) and flag for flag in flags)
            or len(set(flags)) != len(flags)
        ):
            return None
        cigarettes = raw.get("cigarettes", 0)
        if isinstance(cigarettes, bool) or not isinstance(cigarettes, int):
            return None
        if cigarettes < 0:
            return None
        deaths = raw.get("deaths", 0)
        if isinstance(deaths, bool) or not isinstance(deaths, int):
            return None
        if deaths < 0:
            return None
        spoken = raw.get("spoken", [])
        if not isinstance(spoken, list):
            return None
        entries = []
        for entry in spoken:
            if (not isinstance(entry, list) or len(entry) != 4
                    or not isinstance(entry[0], str)
                    or not isinstance(entry[3], str)
                    or any(isinstance(v, bool) or not isinstance(v, int)
                           for v in entry[1:3])):
                return None
            entries.append(tuple(entry))
        return SaveRecord(checkpoint_id, sanity, tuple(sorted(flags)),
                          cigarettes, deaths, tuple(sorted(set(entries))))

    def write(self, record: SaveRecord) -> bool:
        """Atomically replace the save; return False if storage is unavailable."""
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary.write_text(
                json.dumps(record.to_json(), indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            temporary.replace(self.path)
        except OSError:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
            return False
        return True

    def delete(self) -> None:
        """Clear the single slot for NEW GAME; failure is non-fatal."""
        try:
            self.path.unlink(missing_ok=True)
        except OSError:
            pass
