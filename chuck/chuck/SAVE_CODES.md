# Save codes

The plan for replacing the Ashtray save with a code the player holds, so
the game can be saved and resumed in a browser with no file system.

Nothing here is built yet. This is the shape to build to, and the record
of why each decision went the way it did, so a later session does not
re-open settled ground.

---

## 1. What changes, and what does not

**Changes.** The save is written from a menu, not by touching an object.
It is a twelve-character code the player copies, and pasting it back resumes
the game. The resume point is the door Chuck last walked in by, not an
Ashtray.

**Does not change.** Death still returns him to a nearby point in the
same map, with the same peaceful transition. The Ashtray goes entirely
-- object, interaction and writing -- and the door he came in by becomes
both the save point and the respawn point. Measured, that costs a median
of 1.7 tiles of extra walking against today (§5).

**Not doing.** Save-anywhere. The code names an entrance, not a
position, which keeps the record tiny and means a save can never be
taken in the middle of an encounter — no storing whether the Astral seal
has shut, how much of the pit fiend is left, or where the trio's
conversation has got to.

---

## 2. What has to survive a save

Everything the current `SaveRecord` carries, minus two fields:

| what | today | in the code |
| --- | --- | --- |
| where he is | `checkpoint_id` (76 Ashtrays) | entry index (147 runtime entries) |
| what has happened | `progress_flags`, 25 of them | the same 25, as a bitfield |
| cigarettes | `cigarettes` | same |
| deaths | `deaths` | same |
| who has introduced themselves | `spoken`, positional tuples | **dropped**, see below |
| sanity | `sanity` 1..100 | **dropped**, resumes on a fresh 60 |

Sanity went for length, and is the one deliberate loss: see §3. A code
resumes at a door on a fresh 60, which is what walking in gives.

`spoken` is `(map, x, y, line)` per NPC who has said their first words.
It is the one unbounded field and the only one that needs a positional
key. Dropping it costs a resumed game one repeated introduction per NPC
met before the save — cosmetic — and removes the only part of the record
that cannot be a fixed-width field. The autosave path (§7) keeps it, so
this only affects a game resumed from a pasted code.

### Counts that must stay honest

**Chests: free.** `premium_cartons_collected()` counts how many of three
flags are set. It is derived, not tallied, so it is exact no matter how
many codes a player keeps. Opening an opened chest sets an already-set
flag. Nothing to build.

**Deaths: rewindable, and that is accepted.** A counter that only goes
up can always be rolled back by pasting an older code, because the code
*is* the state. Decided: accept it. Deaths are a curiosity on the
credits roll and no amount of engineering closes the hole.

**Cigarettes: already farmable, unrelated to this work.** Loose
cigarettes and breakable grass spawn unconditionally from the map
(`world_scene.py`, ~193 sources game-wide), so leaving a map and
re-entering it respawns all of them. That hole exists today. It does not
matter while cigarettes have no spend sink. If they ever get one, the
fix is a per-pickup collected bitfield (+193 bits, roughly doubling the
code length), not anything about saves.

---

## 3. Field layout

| field | bits | range |
| --- | --- | --- |
| entry | 8 | one of 147 runtime entries |
| progress flags | 25 | one bit each |
| cigarettes | 13 | 0..8191 |
| deaths | 9 | 0..511 |
| **payload** | **55** | exactly 11 base32 characters |
| parity | 5 | 1 character, weighted Reed–Solomon over GF(32) |
| **total** | **60** | **12 characters** |

Written in groups of four: `KMW9-J6ZP-2T5D`.

### The floor, and what was spent getting to it

Thirty-three of those bits cannot be removed by any encoding:

- **entry, 8 bits.** 147 doors. Seven bits hold 128 and eight hold 256;
  the spare slots are the append room the registry needs anyway.
- **flags, 25 bits.** The 25 progress flags are genuinely independent.
  Ten of them look cosmetic — `deck_jeffries_met`, the four
  `cabin_entity_*_spoken` — and are not: seven gate the captain
  confrontation and four gate the counter map, which gates the desert
  transition. Three pairs are the premium cartons. Nor can they be
  derived from the entry: the authored `required_flags` on a checkpoint
  are minimal gates, not full prerequisites, and measured across all
  147 doors they pin down at most 6 of the 25.

So 33 bits before a single cigarette. Everything above that floor was
cut to reach twelve characters:

| cut | cost |
| --- | --- |
| sanity, 7 bits | a code resumes on a fresh 60, as walking in does |
| format version, 4 bits | moved into the parity constant (below) |
| cigarettes 16 → 13 | caps at 8191 instead of 65535 |
| deaths 10 → 9 | caps at 511 instead of 1023 |
| parity 2 chars → 1 | see below |

Both counters still clamp on write rather than overflow, because loose
cigarettes respawn with their map and the total has no real ceiling.
A wrap to nothing would be worse than a stop.

### Why Crockford base32

Case-insensitive, and it omits I, L, O and U, so there is no reading a
code off a screenshot and guessing between `1` and `l`. All 32 of its
characters are already in `GLYPH_ORDER`, so the bitmap font needs no new
glyphs to print one.

Not base64: it is case-sensitive and uses `+`, `/` and `=`, all of which
are miserable to retype.

### Why one check character

The point of the check is that a mistyped code says "that is not a code"
instead of loading a corrupted game. One Reed–Solomon check symbol over
GF(32), weighted by position, buys exactly two guarantees:

| what the player did | what happens |
| --- | --- |
| one character wrong | always caught |
| two characters swapped | always caught |
| two or more characters wrong | ~1 in 32 gets through |
| a code made up from nothing | ~1 in 56 is a real save |

The first two are the mistakes a player actually makes when retyping,
and they are guarantees rather than probabilities: a single wrong symbol
leaves the syndrome equal to that error times a non-zero weight, and a
swap leaves it equal to the difference of the two symbols times the
difference of their weights. The weighting is what catches the swap; a
plain sum would be blind to it.

The rest is the price of the character. Both figures are measured in
`tests/test_save_code.py` rather than assumed, so they stay decisions.

### This is not tamper-proof, deliberately

Fifty-five bits with a five-bit check, and the mask shipping inside the
game, means a determined player can work out how to edit a code. That
was chosen: **a code short enough to write on the back of a hand is
worth more than a code nobody can edit.** CHUCK is single-player, the
save is the player's own, and a save the player can carry is the point
of the exercise. No amount of checksum would have changed this anyway —
in a browser build the whole codec sits in readable JavaScript.

The mask is there so a code looks like a code rather than like its own
field layout. It is symbol-wise, so it cannot turn one wrong character
into two, and both guarantees above survive it.

### Versions, without a version field

There is no version field. The format's version is the constant the
parity is seeded with, so a code from a later format fails this build's
check and is refused as mistyped — 31 times in 32, with the last one
decoding as some other save. That is weaker than naming the version, and
it is what twelve characters can afford.

**So: change the seed whenever the layout changes.** A layout change
without a seed change would have yesterday's codes read as today's, in
silence. `tests/test_save_code.py` holds the golden code, which fails the
moment either one moves.

---

## 4. The registries, and the discipline they need

Two ordered lists decide what a code means:

* **`SAVE_ENTRIES`** — the runtime entries, in a frozen order. 147 of
  them today; the field holds 256.
* **`SAVE_FLAGS`** — the 25 progress flags, in a frozen order.

**Append only. Never reorder, never remove.** Position *is* the wire
format: move one entry and every code ever written silently resumes
somewhere else. A retired entry keeps its slot as a tombstone that
decodes to "this code is too old".

This is enforced by test, not by memory (§8). It is the single most
dangerous thing in this design, because getting it wrong is silent.

The registries live in their own module and are derived from nothing —
not from iteration order over `CHECKPOINTS`, not from a set, not from a
glob. Explicit tuples, written down.

---

## 5. The map entrance is the save point AND the respawn point

One rule, for the player and in the code: **die, and reappear at the
door you came in by.** No object, no interaction, no waypoints, nothing
to learn, nothing extra in the save code.

An earlier draft of this spec split the two apart and kept the Ashtray
positions as invisible respawn waypoints, on the strength of a
measurement that turned out to be the wrong measurement. It is recorded
here because the wrong number is persuasive and somebody will find it
again.

**The wrong measurement.** Distance from each Ashtray to the nearest
entrance on its map: median 5.2 tiles, but a tail out to 40, and 15 of
them more than 10 tiles out on maps with something that can kill him.
From which it looks as though moving the respawn to the door adds up to
40 tiles of walking back, through whatever has respawned.

**The right one.** That is not what it adds, because the *fights* are
deep in the maps too. The walk back from an Ashtray to the furthest
enemy on its map is already long — median 19 tiles for a combat map. The
question is only how much longer the door makes it:

| | tiles |
| --- | ---: |
| median extra walk, all 36 combat maps | **1.7** |
| mean | 3.1 |
| maps where it changes nothing at all | 16 of 36 |
| worst case (temple_shrine) | 15.8 |

A median of under two tiles. The Ashtrays sit near the entrances
already, so respawning at the entrance instead of the Ashtray is, for
most of the game, the same spot.

Two maps are worth remembering if deaths there start to grate:
`temple_shrine` (+15.8 tiles) and `desert_undead_ruins` (+14.0). The fix
if it ever matters is to move that map's arrival, which is one
coordinate — not to bring back a second mechanic.

### The Ashtray goes completely

Not just as a save mechanic: out of the world, out of the writing.

* the `AstralAnchor` entity and its sprite, and the attunement interact
* the `anchor:` markers in the maps, and the checkpoint definitions
  behind them
* `config.HINT_ANCHOR` — the tutorial hint "Ashtrays save your progress"
* `pause_scene.CONTROLS_NOTE` — the same line on the controls page
* the pause menu's quit warning, "Anything since your last Ashtray..."
* `AstralAnchorSystem` keeps its job (it already tracks a respawn point
  set on map entry) and loses the half that advances it

The end credits mention no Ashtray, so there is nothing to remove there.

**Left alone unless Sean says otherwise:** Zephyros's lines in
`data/dialogue/zephyros.json` — "...or whether they've already been
smashed together in the ashtray. But you, Chuck... You're part of the
ashtray." That is the cigarette metaphor the whole game is named after,
not a reference to the save object, and the save rework is no reason to
lose it.

## 6. What the player sees

**Pause menu**, between VOLUME and FULLSCREEN:

```
SAVE GAME     ->  a panel showing the code, and COPY / BACK
```

**Title menu**, replacing CONTINUE when there is no local save, and
alongside it when there is:

```
LOAD CODE     ->  an entry field, and PASTE / OK / BACK
```

Entry needs a text field, which the game does not have yet: the pause
and title scenes are both fixed option lists. A character picker (dial
through the 32 glyphs) is more code and more tedious than accepting
keyboard input and, in a browser, a paste. Budget for a small reusable
`CodeEntry` widget.

Copy and paste are platform calls — `pygame.scrap` on desktop, the
clipboard API in a browser build. Both need a fallback: show the code
large enough to read and type.

---

## 7. Local saves stay, and stay primary

The code is for *moving* a save — between devices, or back after a
browser clears its storage. It is not the everyday path.

* Desktop: `save.json` as now.
* Browser: the same record in localStorage.

Both keep `spoken`, which the code drops. Both are written on entering a
map. The code is produced on demand from the same record.

### Rollback safety

`SAVE_VERSION` is currently 1, and the loader rejects any record whose
version is not an exact match. **Bump it to 2** rather than reusing 1,
and write the new format to a new filename. Then an old build ignores a
new-format file instead of choking on it, and rolling the code back
leaves the player's existing `save.json` sitting there to be picked up
again. Git can revert the code; it cannot revert a file on disk that the
game has already overwritten.

---

## 8. Tests

The format:

* round trip — every field at its limits encodes and decodes unchanged
* a mistyped character fails the checksum rather than decoding
* lower case, spaces and missing group dashes all decode
* a code from a future version number is rejected cleanly
* **golden code** — one code committed as a literal, with the record it
  must decode to. This is the test that catches a registry reorder.

The registries:

* `SAVE_ENTRIES` and `SAVE_FLAGS` match a committed hash of their
  contents; changing one in place fails, appending to it does not
* every entry in `SAVE_ENTRIES` is a real checkpoint id
* every flag in `SAVE_FLAGS` is in `KNOWN_PROGRESS_FLAGS`, and every
  known flag is in `SAVE_FLAGS`

The behaviour:

* a code taken after opening a chest, loaded twice, still reads 1/3 —
  the exploit this was meant to prevent, pinned
* loading a code puts Chuck at the named entrance with the named sanity,
  flags, cigarettes and deaths
* death still respawns at the nearest armed waypoint, at the same
  distances as today — a regression test over all 76 positions
* a save cannot be taken during an encounter (there is no entry to name)

---

## 9. Commits

Small enough to revert one at a time, in this order:

1. `SAVE_ENTRIES` / `SAVE_FLAGS` registries and their discipline tests.
   No behaviour change.
2. The codec — encode, decode, checksum, golden test. Pure functions,
   no game state.
3. `SaveRecord` v2: drop `spoken` from the code path, bump the version,
   new filename.
4. Respawn moves to the map entrance; the save no longer depends on
   Ashtrays.
5. `CodeEntry` widget.
6. Menu wiring: SAVE GAME, LOAD CODE.
7. Remove the Ashtray: entity, sprite, map markers, checkpoint
   definitions, tutorial hint, controls note, quit warning.

Branch `save-codes`, off the tag `pre-save-rework`. Change course before
it merges and the branch is deleted; merge it and regret it and
`git revert -m 1` undoes the lot.
