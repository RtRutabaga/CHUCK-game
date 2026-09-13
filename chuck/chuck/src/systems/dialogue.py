"""Dialogue.

Responsibilities:
    * Load dialogue text from data/dialogue/*.json — writing lives in
      data files, never in code, so writing sessions touch zero Python.
    * Serve a linear sequence of lines by id. The DialogueScene owns
      playback; the DialogueBox owns presentation.

File format: each JSON file maps ids to line lists:
    { "dock_worker": ["Morning.", "..."] }
All files in the directory are merged; a duplicate id across files is
a loud error (silent shadowing of writing is unacceptable), as is
requesting an id that doesn't exist.

Scope rules (Game Bible / Phase One plan):
    * Linear conversations ONLY. No trees, no choices, no quest flags.
    * Chuck never has dialogue lines. Ever.

Tone rules:
    * Deadpan. Grounded. Strange things stated as ordinary and never
      elaborated on.

Pure Python (json + pathlib) — unit-testable without pygame.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.core import config


class DialogueSystem:
    """Loads and serves dialogue sequences by id."""

    def __init__(self, dialogue_dir: str | Path | None = None) -> None:
        directory = Path(dialogue_dir) if dialogue_dir else config.DIALOGUE_DIR
        self._dialogues: dict[str, list[str]] = {}
        for path in sorted(directory.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            for dialogue_id, lines in data.items():
                if dialogue_id in self._dialogues:
                    raise ValueError(
                        f"Duplicate dialogue id {dialogue_id!r} in {path.name}"
                    )
                if not isinstance(lines, list) or not all(
                    isinstance(line, str) for line in lines
                ) or not lines:
                    raise ValueError(
                        f"Dialogue {dialogue_id!r} in {path.name} must be a "
                        f"non-empty list of strings"
                    )
                self._dialogues[dialogue_id] = lines

    def has(self, dialogue_id: str) -> bool:
        return dialogue_id in self._dialogues

    def get(self, dialogue_id: str) -> list[str]:
        """Return the ordered lines for a dialogue id. Loud if missing."""
        if dialogue_id not in self._dialogues:
            known = ", ".join(sorted(self._dialogues)) or "(none loaded)"
            raise KeyError(
                f"Unknown dialogue id {dialogue_id!r}. Known ids: {known}"
            )
        return list(self._dialogues[dialogue_id])
