# Agent Handoff

## Repository State

- Branch: main
- Base commit before this pass: `4667e3f` (big-block rubble)
- Current work: chaotic, many-angled collapse rubble (session 143)
- Active phase: Phase 6 — The Jungle Temple (`PHASE-6.md`)

## Completed This Pass

Made the rubble look like a genuine roof collapse, not rows of blocks:

- temple_rubble_block is now 12 variants. rubble_block(variant) seeds a
  per-variant RNG and drops one or two broken chunks (_stone_chunk,
  lit from above) at a random offset and tumble-rotation (±24°) inside a
  44x36 canvas. Because props anchor bottom-center per tile, the
  off-centre chunks break the grid, and the per-tile variant index
  (col*31+row*17)%12 scatters the angles — so no orderly rows.
- generate_temple_rubble.py places debris in irregular collapse-piles:
  density is a 0.18 base scatter plus up to +0.68 near ~14 collapse
  centres, so blocks heap thickly where the roof dropped and thin out
  between. ~270 blocks + ~45 drums, 214 Astral, the paved lane still
  clear (connectivity re-asserted).
- 8 new block PNGs + 4 updated; no churn elsewhere. All 55 suites pass.

## Previous Pass (session 142, commit 4667e3f)

Rebuilt the rubble map's debris as big broken blocks:

- New prop temple_rubble_block — four chunky 3/4-view broken-masonry
  sprites (tools/generate_temple_props.py rubble_block(); 30x24; lit top
  face, shadowed side, cracks, a broken-off corner, moss). Registered in
  prop.py _SPRITES and as tile 'ß' (solid, under '·').
- tools/generate_temple_rubble.py now fills the chamber with a dense
  field of these big blocks (~360) plus a scatter of smaller column
  drums (~45) for scale. Torches, cracked stelae ('‡'), and flat
  wall-tile boulders ('█') were all removed, so it reads as one
  consistent field of collapsed masonry with the clean paved '≡' lane
  threading through. temple_column is unchanged → temple dressing maps
  untouched.
- Only the four new PNGs were written (no churn on the other prop art).
- test_phase6_temple_rubble.py now asserts the blocks dominate and there
  are no torches.

## Previous Pass (session 141, commit 42c7208)

Reworked the rubble exit and the escape cutscene per playtest notes:

- The rubble exit is now an "Enter crevice?" YES/NO interaction, not a
  walk-over exit. data/choices/temple_rubble.json ("crevice": YES →
  goto ship_deck, NO closes); ChoiceTrigger "crevice" (2x2); a marker
  Ҏ on the paved lane one tile above the ∇ crawl mouth. The ∇ walk-exit
  was removed from AREA_WALK_EXITS; YES's goto ship_deck is intercepted
  in WorldScene's _pending_map handler to replace the world with the
  escape cutscene (so the interception moved from the walk-exit block to
  the pending-map load).
- The escape cutscene is now wordless — the three narration captions and
  the caption drawing were removed, shortening the timeline (HOLD_END
  11.4, FADE_END 12.2).
- Its emergence tableau was rebuilt: the open hull breach became a
  wooden hull WALL set with three round brass-rimmed portholes, each
  showing a sunlit, lighter-blue sea over a horizon — plainly a ship's
  interior, the sea framed in circles. (_draw_hold / new _draw_porthole;
  lighter sea palette.)
- Tests: test_phase6_escape_cutscene.py now asserts wordlessness and the
  shorter timeline; the rubble test asserts the crevice choice trigger
  (no walk-exit); the ship-deck test drives YES → cutscene → deck.

## Previous Pass (session 140, commit ce4c4f2)

The escape cutscene, which ends Phase 6:

- src/scenes/escape_cutscene_scene.py (new): EscapeCutsceneScene, a
  contained input-free Scene modelled on FallingCutsceneScene. Chuck
  crawls a tight stone tunnel toward a growing blade of daylight
  (receding stone rings for forward motion, a corner vignette for
  tightness, scrape sfx), the light whites out the screen, and he
  emerges into the wooden hold with the open sea beyond the hull breach
  (colours matched to the ship_deck map). The sea theme
  (waterdeep_docks.wav) swells in at the emergence. Three timed
  narration captions land the beat, then it fades to black and hands off
  to the playable deck via load_checkpoint("ship_deck", sanity=...),
  carrying Chuck's Sanity across.
- src/scenes/world_scene.py: the rubble crawlspace walk-exit now
  replaces the world with the cutscene instead of loading ship_deck
  directly (mirrors the sky-fall → FallingCutsceneScene trigger).
- PHASE-6.md: "The cutscene ends aboard a ship at sea" is now checked.
- Tests: test_phase6_escape_cutscene.py (3, new — captions, draws every
  phase input-free, hands off preserving Sanity); the ship-deck crawl
  test now asserts it routes through the cutscene.

## Previous Pass (session 139, commit b1a2b1d)

temple_rubble was rebuilt to look like the temple's ceiling has caved in:

- The chamber is now choked with ~460 pieces of fallen-stone debris —
  toppled columns ('¬') and cracked leaning stelae ('‡') scattered as
  separate props at ~58% density off the route (so it reads as rubble
  on the floor, not a wall), plus a few lone '█' boulders ringed by
  floor. Split by 15 distinct blocks of Astral Sea (~213 'V'). Off the
  route it is almost impassable.
- One intact paved lane ('≡', the temple's own processional tile) winds
  torch-lit from the from_fireball arrival, past the rubble ashtray, to
  the crawlspace mouth. Against the debris the clean lane is unmistakably
  the way out. The Ѣ/Ѥ marker unders changed to '≡' so they sit
  seamlessly on it.
- tools/generate_temple_rubble.py was rewritten (curated Astral blocks,
  a lane-polyline clear + pave, a deterministic debris scatter, lone
  boulders, flanking torches) and still asserts arrival → anchor →
  crawlspace connectivity on foot before writing.

## Previous Pass (session 138, commit 2968d01)

The rubble got its one way out, leading to the ship — the Phase 6 → 7
boundary:

- The crawlspace exit: a narrow mouth ('∇', the established threshold
  tile) is carved into temple_rubble's south wall at the foot of a
  cleared right-side lane. tools/generate_temple_rubble.py now protects
  that lane (col 34, rows 20-27) and asserts the mouth is reachable on
  foot before writing. Walking onto it transitions to the ship
  (AREA_WALK_EXITS["temple_rubble","∇"] → ship_deck / from_crawlspace).
- ship_deck (assets/maps/ship_deck.txt, 30x18): a cramped wooden hold
  on the docks tileset — plank floor, lashed barrels and crates — with
  a jagged breach in the hull (top) opening onto the open sea (water).
  Chuck arrives at the crawl mouth in the deck floor and walks up toward
  the sea reveal. No onward exit (Phase 7 is unbuilt).
- Wiring: new markers Ҋ (arrival:from_crawlspace) / Ҍ
  (anchor:ship_deck_anchor); MAP_TILESET["ship_deck"] = "docks";
  AREA_MUSIC["ship_deck"] = "waterdeep_docks.wav" (the sea theme
  returns); checkpoints "Ship 1" (runtime, dev-visible, fade_in) +
  "Ship Ashtray".

## Files Changed

- tools/generate_temple_rubble.py (full rewrite: curated Astral blocks,
  lane pave, debris scatter, boulders, torches),
  assets/maps/temple_rubble.txt (regenerated), src/world/tilemap.py
  (Ѣ/Ѥ marker unders → '≡'), tests/test_phase6_temple_rubble.py (the
  broken-chamber test now locks in the debris count, the paved lane, and
  the raised Astral count).

## Verification Performed

- All 55 suites pass (per-suite timeouts; nothing hangs).
- Headless: stepping onto the rubble crawlspace replaces the world with
  EscapeCutsceneScene; playing it through hands off to ship_deck at the
  from_crawlspace arrival with Sanity preserved (40 → 40).
- Screenshots: the crawl (a receding stone tunnel to the daylight, Chuck
  crawling, vignetted corners) and the emergence (the wooden hold, the
  sea through the hull breach, Chuck looking up, a narration caption).

## Known Issues

- None known from this pass.

## Scope Notes

- Phase 6 is now content-complete end to end (entrance → temple maps →
  boss battle → Fireball → rubble → crawlspace → escape cutscene →
  ship). What remains is polish/handoff: a distinct escape-cutscene
  music cue (it currently reuses the sea theme), and Phase 7 gameplay
  aboard the ship (the deck is a free-roam room with no onward exit).

## Recommended Next Bounded Task

- Begin Phase 7 (see the Phase 7 doc when it exists): the first playable
  beat aboard the ship — or, if staying in Phase 6, compose a dedicated
  escape-cutscene music cue (a short one-shot like fall_to_chult.wav)
  and swap EscapeCutsceneScene's SEA_MUSIC over to it.
