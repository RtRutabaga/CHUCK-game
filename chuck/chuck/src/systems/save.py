"""What a save is made of.

There is no save file any more. A save is a twelve-character code the
player holds (`save_code`), and this is the record that code is written
from and read back into. Nothing here touches a disk.

The file went with CONTINUE. There was never an autosave -- only the
pause menu wrote a save -- so a slot on disk was never better than the
player's last deliberate save, and it cost a second persistence system
that had to agree with the code and could not in a browser. See
`docs/development/DECISIONS.md`.

Two fields are in the record but not in a code, because a code is
twelve characters and these are what did not fit:

    sanity    a resumed game starts at config.SANITY_START
    spoken    everyone Chuck has met introduces themselves again
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SaveRecord:
    checkpoint_id: str
    sanity: int
    progress_flags: tuple[str, ...]
    # The overall-game cigarette total (session 128).
    cigarettes: int = 0
    # Deaths this playthrough.
    deaths: int = 0
    # Who Chuck has already had a first word from, as (map, x, y, line)
    # -- the second-word memory (WorldScene._second_word). Held for the
    # session only; a code does not carry it.
    spoken: tuple[tuple[str, int, int, str], ...] = ()
