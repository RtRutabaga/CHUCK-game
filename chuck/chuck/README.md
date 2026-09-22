# CHUCK

A top-down 2D action-adventure RPG (Python + Pygame CE, pixel art, tile-based).

You control Chuck: a one-foot-tall fey rat in an oversized purple jacket,
quietly walking through a world built for humans. See the Game Bible for
design authority.

## Running

```bash
pip install -r requirements.txt
python main.py
```

The game opens at a native-resolution title menu: NEW GAME, LOAD CODE,
CONTROLS.

**There are no save files.** SAVE GAME in the pause menu gives a
twelve-character code and LOAD CODE takes one back, on any machine and in any
build. The Ashtray checkpoints this file used to describe, and the CONTINUE
option that went with them, were replaced by that system; `save.json` holds
settings and the current slot, not a save the player can rely on. A code is the
save.

## Building the Windows demo

Build on Windows with Python 3.12 or newer:

```powershell
py -m pip install -r requirements-build.txt
py -m PyInstaller --clean --noconfirm CHUCK.spec
```

The shareable single-file build is written to `dist/CHUCK-demo.exe`. Friends do
not need Python, Pygame, or the repository; they can run that EXE directly. The
first launch may take a moment while the one-file bundle extracts. Because this
is an unsigned personal build, Windows SmartScreen may ask the recipient to
confirm that they want to run it. If the game crashes, `crash_log.txt` is written
beside the EXE.

PHASE 2 IN PROGRESS. An armored city guard now posts the east edge of
the upper plaza — the way out of the docks. The map layout already
ends the road there, so he needs no gate and no barrier: he simply
stands, and interacting gets "Stick to the docks, rat."

Tutorial hints (temporary, Waterdeep + sewer only): a pale line of text
appears near the top of the screen — "Press E to interact" — whenever
Chuck is in reach of someone or something he can talk to, and vanishes
when he steps away. The hint and the interact key read the same
in-reach search (src/systems/interaction.py), so the hint can never
promise an interaction the key won't deliver.

A sewer grate sits in the plaza near the guard. Interacting with it
asks a question — "Jump into the sewer?" — with YES / NO options and a
caret you move with up/down and commit with E. Choices are data
(data/choices/*.json, validated loudly), so any future decision anywhere
in the game is a JSON entry, not new code. An option can speak dialogue,
carry Chuck to another map (its `goto`), or silently close: YES drops
him straight into the sewer, wordlessly, while NO simply closes the box.
Any scene rebuilds into another area via
WorldScene.load_map(), and each map draws with its own tileset
(tileset_layout: docks.png, sewer.png). The sewer (assets/maps/sewer.txt)
is a long corrupted descent with its own art — brick walls, dirt and mud,
flowing drainage, and Astral blocks — plus its own eerie, funky theme.
Its iron outflow returns Chuck to Waterdeep's south pier.

Current state (after session 13): the docks are lived-in. Bobert
sleeps in his barrel beside Chuck's spawn — gray beard over the rim,
arms folded, eyes shut; solid scenery, never named, never interactable
(map tile 'B'). Cigarettes are drawn sprites now (paper, ember, a wisp
of smoke) and the Astral Anchor presents as an ashtray — cold gray ash
with a dead stub when dormant, a live ember glowing warm (with a wisp
of smoke) once attuned. Nothing on screen is a placeholder
rectangle anymore except the HUD meter, which is a cigarette on
purpose. A dock worker
stands on the street near the tavern — walk up, face him, press E (or
Space/Enter): he turns to look down at Chuck and a dialogue panel opens
with a typewriter reveal. E completes the current line instantly or
advances to the next; the last press (or ESC) closes it. The world
freezes during conversation — a held breath — and resumes after. Chuck,
as ever, says nothing. Dialogue text lives in data/dialogue/*.json;
writing new lines touches zero Python. Everything from session 7 (cat,
anchor, quiet respawn) still stands. ESC in the world quits.

Tests: `python -m tests.test_collision`, `python -m tests.test_tilemap`,
`python -m tests.test_camera`, `python -m tests.test_animation`,
`python -m tests.test_sanity`, `python -m tests.test_hazard`,
`python -m tests.test_dialogue`, `python -m tests.test_audio` (all
pure Python, no pygame needed). See PROJECT_STATUS.md for full status.

Sprites are generated from text grids (shared renderer in
`tools/spritegen.py`): edit the character grids in
`tools/generate_chuck_sprites.py`, `tools/generate_cat_sprites.py`, or
`tools/generate_npc_sprites.py` (or the font in
`tools/generate_font.py`) and re-run them (needs `pip install pillow`, dev-only). The shipped
PNGs are already built — Pillow is NOT needed to play.

## Project layout

```
main.py                 Entry point. Stays tiny forever.
assets/                 Art, audio, maps, fonts (data, no code)
data/dialogue/          Dialogue text (writing lives here, never in .py files)
src/
  core/                 Engine plumbing
    game.py             Window + main loop; delegates everything else
    config.py           All tunable constants (single source of truth)
    input.py            Named actions (gameplay never touches keycodes)
    assets.py           Cached asset loading
    scene_manager.py    Scene stack (world + overlays like dialogue)
  scenes/               Game modes (boot, world; later: dialogue overlay, astral transition)
  world/                tilemap.py, camera.py, collision.py
  entities/             entity.py (base), player.py (Chuck), npc.py, pickup.py
  systems/              sanity.py, astral_anchor.py, dialogue.py, audio.py
  ui/                   hud.py, dialogue_box.py
```

## Conventions for future sessions

- **One feature per session.** Implement it, run it, polish it, then stop.
- **No monoliths.** New features get new modules; keep files small and testable.
- **Data over code.** Maps, dialogue, and tuning values live in `assets/`,
  `data/`, and `config.py` — not hardcoded in gameplay files.
- **Rendering:** everything draws to the 320x180 native surface, which is
  integer-scaled to the window. Never draw directly to the window.
- **Top-down only.** No jumping, no gravity. (The old "platformer" phase
  doc predates the Game Bible; the Bible wins.)
- **Sanity, not health.** Zero sanity = quiet vanish + respawn at the last
  Astral Anchor. No game-over screens, ever.
- Stubs raise `NotImplementedError` or carry `TODO:` comments marking where
  each future feature lands.

## Map format (placeholder)

Maps are plain text in `assets/maps/`; lines starting with `;` are
comments. Terrain: `#` wall/crate, `o` barrel, `~` water (all solid);
`.` floor, `,` stone, `=` dock planks (walkable). Markers (things ON a
tile, each declaring its under-terrain): `C` Chuck's spawn (on planks),
`c` cigarette (on stone), `j` cigarette (on planks), `K` patrolling cat
(on stone), `A` Astral Anchor (on stone), `N` dock worker NPC (on stone). Unknown characters
and markers over solid terrain fail loudly with row/col. The legend lives in
`src/world/tilemap.py` and will grow (or be replaced by Tiled) when real
art arrives; `is_solid` / `spawn_points` / `draw_ground` / `draw_overhead`
are the stable interface.

## Suggested next sessions (one each)

1. ~~Player movement + collision~~ ✅ done (session 2)
2. ~~First tilemap: Waterdeep Docks layout (placeholder tiles)~~ ✅ done (session 3; expanded to 2x2 screens in session 4)
3. ~~Camera follow + map clamping~~ ✅ done (session 4)
4. ~~Chuck sprites + animation~~ ✅ done (session 5)
5. ~~Cigarettes + sanity meter HUD~~ ✅ done (session 6)
6. ~~One hazard (a cat), vanish/respawn at an Astral Anchor~~ ✅ done (session 7)
7. ~~One NPC + dialogue box~~ ✅ done (session 8)
8. ~~Ambient audio pass~~ ✅ done (session 9: synth engine + full SFX set)
9. ~~The Waterdeep Docks theme~~ ✅ done (session 10; ambience removed, E-key interaction fixed)
10. ~~Y-sorted depth drawing + standing props~~ ✅ done (session 11)
11. ~~The docks tileset art pass~~ ✅ done (session 12)
12. ~~Bobert + cigarette/anchor sprite pass~~ ✅ done (session 13)
13. ~~Expand the docks inland + overhead layer~~ ✅ done (session 14)
14. ~~Bobert's snore + readable HEROD sign~~ ✅ done (session 15; quiet music variation cut by direction)
15. ~~Size pass: door, piers, awning~~ ✅ done (session 16, playtest-driven)
16. ~~Tavern exterior art pass (facade reference)~~ ✅ done (session 17)
17. ~~District wall art pass (castle-wall reference)~~ ✅ done (session 18)
18. Continue the playtest & polish pass (the last Phase One item)
