# Save codes

The plan for replacing the Ashtray save with a code the player holds, so
the game can be saved and resumed in a browser with no file system.

Nothing here is built yet. This is the shape to build to, and the record
of why each decision went the way it did, so a later session does not
re-open settled ground.

---

## 1. What changes, and what does not

**Changes.** The save is written from a menu, not by touching an object.
It is a short text code the player copies, and pasting it back resumes
the game. The resume point is the door Chuck last walked in by, not an
Ashtray.

**Does not change.** Death still returns him to a nearby point in the
same map, at the same distances as today, with the same peaceful
transition. The Ashtray *object* goes; the respawn behaviour it provided
stays, as invisible waypoints (§5).

**Not doing.** Save-anywhere. The code names an entrance, not a
position, which keeps the record tiny and means a save can never be
taken in the middle of an encounter — no storing whether the Astral seal
has shut, how much of the pit fiend is left, or where the trio's
conversation has got to.

---

## 2. What has to survive a save

Everything the current `SaveRecord` carries, minus one field:

| what | today | in the code |
| --- | --- | --- |
| where he is | `checkpoint_id` (76 Ashtrays) | entry index (147 runtime entries) |
| sanity | `sanity` 1..100 | same |
| what has happened | `progress_flags`, 25 of them | the same 25, as a bitfield |
| cigarettes | `cigarettes` | same |
| deaths | `deaths` | same |
| who has introduced themselves | `spoken`, positional tuples | **dropped**, see below |

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
| format version | 4 | 0..15 |
| entry | 8 | one of 147 runtime entries |
| sanity | 7 | 0..100 |
| progress flags | 25 | one bit each |
| cigarettes | 16 | 0..65535 |
| deaths | 10 | 0..1023 |
| checksum | 32 | truncated HMAC |
| **total** | **102** | 13 bytes |

13 bytes is **21 characters** of Crockford base32, written in groups of
five: `X7B3K-9QW2M-4XH8V-NP2RT-C`.

Sizing notes: the 16-bit cigarette field caps at 65535, which the farm
above could exceed in a long session — clamp on write rather than
overflow. Deaths clamp at 1023 for the same reason.

### Why Crockford base32

Case-insensitive, and it omits I, L, O and U, so there is no reading a
code off a screenshot and guessing between `1` and `l`. All 32 of its
characters are already in `GLYPH_ORDER`, so the bitmap font needs no new
glyphs to print one.

Not base64: it is case-sensitive and uses `+`, `/` and `=`, all of which
are miserable to retype.

### Why sign it at all

A 32-bit truncated HMAC catches typos and stops a casual edit. It is not
security: the key ships inside the game, and in a browser build it sits
in readable JavaScript. A single-player game with a player-held save
cannot be made tamper-proof, and the effort spent pretending otherwise
is better spent elsewhere. The point of the checksum is that a mistyped
code says "that is not a code" instead of loading a corrupted game.

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

## 5. Ashtrays become invisible waypoints

The Ashtray does two jobs today: it is the save point *and* the respawn
point. Only the first is being replaced.

Measured, over all 76 of them, the distance from each to the nearest
entrance on its map (the screen is 20x11 tiles):

* median **5.2** tiles, mean 8.7
* 45 of 74 within 6 tiles — for most of the game, respawning at the
  entrance instead is a difference of a few steps
* but 15 are both more than 10 tiles away **and** on a map with
  something that can kill him:

| ashtray | map | tiles | hostiles | hazard tiles |
| --- | --- | ---: | ---: | ---: |
| desert_ruins_anchor | desert_undead_ruins | 40.0 | 10 | 426 |
| modern_city_day_6_anchor | modern_city_day_6 | 28.2 | 9 | 2071 |
| temple_7_anchor | temple_shrine | 21.8 | 12 | 0 |
| ship_lower_hold_anchor | ship_lower_hold | 17.0 | 16 | 0 |
| modern_city_sewer_2_anchor | modern_city_sewer_2 | 17.2 | 6 | 39 |

Dying in the undead ruins under a pure entrance-respawn rule means two
screens of walking back through ten undead. That is a fighting retreat,
not a few steps.

**So:** keep the positions, drop the object. `AstralAnchorSystem`
already tracks a respawn point that is set on map entry and advanced
when Chuck touches an anchor. It keeps doing exactly that; the anchor
positions become invisible waypoints that arm when he walks over them.
Runtime only — never written to the code, so they cost nothing in the
format and change nothing about the tuning that is already there.

**Open question for Sean:** the Ashtray is also fiction — its examine
lines, the cigarette theme, a beat in the credits. "Gone as a save
mechanic" and "gone from the world" are separable. This plan assumes the
first. If the object should disappear visually too, that is a separate
pass over the sprites, the examine lines and the credits.

---

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
4. Waypoints: Ashtray positions become runtime-only respawn arming;
   the save no longer depends on them.
5. `CodeEntry` widget.
6. Menu wiring: SAVE GAME, LOAD CODE.
7. Remove the Ashtray as a save object.

Branch `save-codes`, off the tag `pre-save-rework`. Change course before
it merges and the branch is deleted; merge it and regret it and
`git revert -m 1` undoes the lot.
