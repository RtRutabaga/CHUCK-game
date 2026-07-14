"""Dialogue choices — data, loaded and validated loudly.

A choice is a prompt plus two or more options; picking one plays that
option's dialogue. Choices live in data/choices/*.json, exactly like
dialogue lines live in data/dialogue/*.json:

    {
      "sewer_grate": {
        "prompt": "Jump into the sewer?",
        "options": [
          { "label": "YES", "dialogue": "sewer_grate_yes" },
          { "label": "NO",  "dialogue": "sewer_grate_no"  }
        ]
      }
    }

Content, not code: a new decision anywhere in the game is a JSON entry
and (if it's a prop) one line in PROP_CHOICE.

Malformed data is a loud error at load, never a mystery at runtime.
Pure stdlib — no pygame — so it's unit-tested headless.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import NamedTuple

from src.core import config


class Option(NamedTuple):
    label: str        # what the player reads: "YES"
    dialogue: str     # dialogue id played when chosen


class Choice(NamedTuple):
    prompt: str
    options: list[Option]


class ChoiceSystem:
    """All choices in the game, keyed by id."""

    def __init__(self, choice_dir: str | Path | None = None) -> None:
        directory = Path(choice_dir) if choice_dir else config.CHOICE_DIR
        self._choices: dict[str, Choice] = {}
        if not directory.is_dir():
            raise FileNotFoundError(f"Missing choice directory {directory}")
        for path in sorted(directory.glob("*.json")):
            self._load_file(path)

    def _load_file(self, path: Path) -> None:
        data = json.loads(path.read_text(encoding="utf-8"))
        for choice_id, raw in data.items():
            if choice_id in self._choices:
                raise ValueError(
                    f"Duplicate choice id {choice_id!r} in {path.name}"
                )
            prompt = raw.get("prompt")
            options = raw.get("options")
            if not isinstance(prompt, str) or not prompt.strip():
                raise ValueError(f"{choice_id}: prompt must be a non-empty string")
            if not isinstance(options, list) or len(options) < 2:
                raise ValueError(f"{choice_id}: needs at least two options")
            parsed = []
            for opt in options:
                label = opt.get("label")
                dialogue = opt.get("dialogue")
                if not isinstance(label, str) or not label.strip():
                    raise ValueError(f"{choice_id}: an option has no label")
                if not isinstance(dialogue, str) or not dialogue.strip():
                    raise ValueError(
                        f"{choice_id}: option {label!r} has no dialogue id"
                    )
                parsed.append(Option(label=label, dialogue=dialogue))
            self._choices[choice_id] = Choice(prompt=prompt, options=parsed)

    def get(self, choice_id: str) -> Choice:
        if choice_id not in self._choices:
            known = ", ".join(sorted(self._choices)) or "(none)"
            raise KeyError(f"Unknown choice id {choice_id!r}. Known: {known}")
        return self._choices[choice_id]

    def ids(self) -> list[str]:
        return sorted(self._choices)
