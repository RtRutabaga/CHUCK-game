# PHASE 8 --- PHLEGETHOS

## Status

Phase 7 ends with Chuck falling into the Nine Hells. The arrival cutscene
is already complete. Phase 8 begins with Chuck exploring Phlegethos.

Phase 9 begins in the Feywild.

Implemented so far:

- The Nine Hells fall now hands off to a playable Phlegethos. A dedicated
  phlegethos tileset (cracked basalt, volcanic cliff, worn stone path,
  animated lava, glowing fissures -- basalt/lava palette shared with the
  hell fall) draws the first `phlegethos_arrival` map (44x30): Chuck lands
  from the fall, a worn path winds north past the Ashtray toward the way
  onward (an inert boundary to the next map). Lava is a walkable, lethal
  fall hazard exactly like the Astral Sea (fall.py + collision), and
  enemies treat it as a wall. Checkpoints `Phlegethos 1` (runtime) +
  `Phlegethos Ashtray`; placeholder music (chult.wav) until the dedicated
  infernal theme is composed. Enemies, lava-island jumps, the fortress
  climax, the soundtrack, and the Feywild-river ending are later slices.
- A second connected map and the first two infernal enemies.
  `phlegethos_road` (48x32) climbs north between widening lava and pinches
  to a single-tile stone ledge with lava on both sides -- the phase's first
  real traversal gauntlet. Ash-choked cliff passes ('∇'/'Δ') join it to the
  arrival map both ways, with checkpoints `Phlegethos 2` + its Ashtray and a
  `Phlegethos 1 Return`. Its north pass onward is an inert boundary until
  map 3. **Lemures** are a third `UndeadEnemy` kind -- the Chultan
  zombie/skeleton lifecycle exactly, but the slowest and most durable yet
  (LEMURE_* config) -- and **fire snakes** are a `TempleSnake` variant that
  changes only the sprite sheet, so both reuse their systems wholesale.
- The lava-lake island crossing (`phlegethos_lake`, 44x34) -- the spec's
  called-out set piece. A wall-to-wall molten lake is crossed by eight
  small basalt stepping stones zigzagging north; every gap is EXACTLY one
  lava tile, so each crossing is a single committed hop (the temple Astral
  connector's rule). `tools/generate_phlegethos_lake.py` proves before
  writing that no island touches another island or a shore, that nothing
  safe is stranded, and that the far shore is reachable by walk+hop; the
  test additionally proves the lake canNOT be walked across. Passes join
  it to the road both ways; checkpoints `Phlegethos 3` + Ashtray +
  `Phlegethos 2 Return`. Fire snakes patrol the shores only -- the lake
  itself is pure traversal.
- An east-west low-pressure traversal map now separates the lake from the
  fortress. `phlegethos_rubble_pass` (64x34) turns the route through 127
  dark basalt-and-ember rubble pieces on a broad winding paved lane. A
  cliff-fed 48x96 lava fall empties into a narrow two-tile lava river, crossed
  on one intact basalt slab. Its only enemies are one slow lemure whose pocket
  delays its approach and one slow horned devil kept beyond notice range from
  the required path. The map owns one Ashtray and development-visible
  `Phlegethos 4`; the fortress display advances to `Phlegethos 5` while its
  persisted checkpoint IDs remain stable.
- The Phlegethos soundtrack (`data/music/phlegethos.py` -> phlegethos.wav),
  replacing the jungle placeholder across all five maps. An original 48-bar,
  ~87s loop at 132 BPM in E Phrygian dominant (E F G# A B C D) -- the flat
  second against the raised third gives the exotic infernal heat, and keeps
  it clearly distinct from the temple's D minor and the boss theme's D
  Phrygian. Twelve voices: an uneven tribal tom engine on every bar, a
  throbbing low synth, driving root-fifth bass, struck metal ringing across
  the groove like distant forges, an eerie exotic lead, and a choir texture
  only in the "the environment is alive" section. Its arc rises (bed ->
  lead -> driving -> alive -> full return -> climbing turnaround) so it is
  never slow, ambient-only or mournful. Two reusable instrument voices were
  added for the brief: `metal_hit` (inharmonic struck metal) and
  `low_pulse` (a tremolo'd filtered square). Renders at 0.93 headroom, RMS
  0.183 (level with temple/boss), seam 0.011.
- The fifth map, the fortress approach
  (`phlegethos_fortress_approach`, 48x34), and the
  last enemy. The iron-black fortress wall now closes off the north with
  its gate shut (new `fortress` / `fortress_gate` tileset rows -- the
  interior is not this phase), and a processional lined with brooding
  **infernal idols** (new `phlegethos_statue` prop, eyes lit from within)
  climbs from the south pass to a muster yard. **Horned devils** are a
  `MassiveDinosaur` variant -- the Chultan colossus's gameplay exactly,
  wearing infernal art: a slab-muscled, batwinged, horned soldier dragging
  a barbed iron fork, towering over Chuck. One holds the yard, with lemures,
  fire snakes and spined devils scattered below. Checkpoints `Phlegethos 5`
  + Ashtray + a Rubble Pass return; the gate approach is an inert boundary
  awaiting the climax. This completes the bestiary and the setting's visual
  brief.
- **Spined devils** and **flameskulls**, completing the bestiary's dodge
  hazards. A spined devil never moves: it perches beside a lane and flicks
  burning tail spines across it on a staggered cadence (the temple
  wall-launcher pattern with a visible, menacing owner). Contact merely
  hurts, but *scratching* one instantly defeats Chuck, so the rule reads
  as "never fight this" -- four of them watch the lava road's lanes. A
  flameskull weaves fast around a fixed haunt (bee-like, never a pursuer),
  cannot be cleared by any scratch, and floats over lava as happily as
  stone -- four haunt the lava lake's stepping stones, using lava-under
  markers so they never punch safe tiles into the lake.
- Seventeen of the Chult temple's **breakable terracotta urns** now appear
  across the five Phlegethos maps. Arrival and Lava Road hold three each;
  four sit only on the Lava Lake's safe shores; three sit off the Rubble
  Pass route; four flank the Fortress yard away from its battle aisle. They
  reuse the exact scratch, shard, carton-drop, and map-reset implementation,
  including the standard 20-cigarette carton. None replaces a required route,
  lava stepping stone, checkpoint, or battle marker.
- The fortress muster yard now contains the trio already battling a towering
  **Pit Fiend**. Its 128x128 native silhouette and broad planted shadow now
  dominate the trio's human-scale figures. The existing non-interactive
  battle actor/projectile
  architecture is reused with a dedicated infernal choreographer: the ranger
  fires directly at the Pit Fiend, the wizard drives repeated bolt fans into
  it, the fighter holds the nearby lesser devils, and the fiend answers across
  their lanes. Entry dialogue makes clear that the trio is trying to bind and
  repair the spreading fractures without explaining the collided worlds.
  Chuck remains an observer navigating the crossfire. Astral escalation,
  Feywild river intrusion, and the escape cutscene remain later slices.
- Corrected the Road and Lake Ashtray marker IDs to match their shared
  checkpoint definitions. Both now save and respawn through the same registry
  path as every other checkpoint instead of crashing on contact.
- The fortress battle now triggers a staged **Astral corruption** sequence
  when Chuck crosses into the upper yard. A continuous two-row band appears
  behind him first, cutting off retreat with an unjumpable shared Astral fall
  hazard. Three later waves break inward from alternating sides as jagged,
  deterministic wrong-map fragments. The sequence never opens directly under
  Chuck, preserves a readable central survival spine for the upcoming river
  intrusion, and fully restores/re-arms on death. Phlegethos now includes the
  exact animated Astral tile language used by the sewer, pantry, Chult, and
  temple rather than a new approximation.
- After the third Astral wave, ten hard-edged **Feywild river fragments**
  begin flowing west through staggered fortress-yard lanes. They use a
  distinct blue-green current with moving pixel streaks and recycle beyond the
  map edge. Six seconds later, eighteen additional blocks align across every
  playable arena row and sweep west as one full-height surge. The three
  Astral side waves leave their broad central route open; it is now the river,
  not an unavoidable purple conversion, that forces the ending.
- Any river contact succeeds, whether Chuck walks or jumps into it. Contact
  starts the exact shared fall-hazard shrink/sink animation, gliding Chuck
  toward the moving water's center. Unlike Astral or lava, completion preserves
  Sanity and fades directly into the river cutscene instead of respawning.
- The stable handoff now enters a dedicated, input-free **Feywild river
  cutscene**. A full-black opening slowly reveals a longer river journey:
  Chuck is carried rapidly down a hard-edged blue-green current while infernal
  basalt banks yield to dense, enchanted Feywild growth. Luminous spiral
  plants, glowing flowers, mushrooms, violet/cyan accents, oversized roots,
  and layered leaves give the destination a psychedelic identity without
  leaving the native procedural style. Chuck crosses a short foaming
  waterfall, remains visible through the calmer current, and clearly washes
  prone onto a quiet bank. After a deliberate still beat, he slowly pushes
  himself upright and stands before the final fade to the held Phase 9
  boundary. The scene preserves Sanity, uses the established
  `fall_to_chult.wav` cue, and creates no playable Feywild map or checkpoint.

------------------------------------------------------------------------

# Phase Goal

By the end of this phase the player should:

1. Traverse numerous connected Phlegethos maps.
2. Survive increasingly dangerous infernal enemies.
3. Cross lava hazards and volcanic terrain.
4. Reach the infernal fortress exterior.
5. Witness the trio battling a Pit Fiend.
6. Be forced into a flowing Feywild river block to escape Astral
   corruption.
7. Wash ashore in the Feywild.

------------------------------------------------------------------------

# 1. Visual Direction

Build a larger overworld similar in structure to Chult but significantly
more dangerous. The setting should feature:

- dark basalt
- lava rivers
- worn stone paths
- infernal statues
- fortress exteriors
- volcanic cliffs
- ash
- glowing lava fissures

Maintain the established simple procedural pixel-art style.

------------------------------------------------------------------------

# 2. Gameplay

Progress through multiple connected maps. Traversal remains the primary
gameplay. Major hazards include:

- lava falls
- lava rivers
- projectile enemies
- narrow basalt paths
- jump challenges

Include a sequence where Chuck jumps across small islands over a lava
lake.

------------------------------------------------------------------------

# 3. Enemies

Reuse existing gameplay systems whenever practical.

- **Lemures** (the DnD kind, not the animals) -- reuse zombie/skeleton
  gameplay.
- **Fire Snakes** -- reuse temple-snake gameplay.
- **Spined Devils** -- remain stationary and launch flaming tail spines
  as ranged dodge hazards. Attempting to melee one immediately defeats
  Chuck.
- **Flameskulls** -- rapid weaving movement similar to bees; they
  primarily function as moving dodge hazards.
- **Horned Devils** -- reuse the massive-dinosaur behavior from Chult.

------------------------------------------------------------------------

# 4. Fortress Climax

The final area occurs outside a large infernal fortress. The trio of
adventurers are already battling a Pit Fiend.

- The fighter engages lesser devils.
- The wizard casts powerful spells.
- The female ranger now fires directly at the Pit Fiend.

Chuck is not participating; he survives by avoiding hazards. Dialogue
should make it somewhat clearer that the trio understands the collided
worlds and is actively trying to repair them, without fully explaining
the mystery.

------------------------------------------------------------------------

# 5. Feywild Bleedthrough

Initially Astral Sea blocks appear and cut off Chuck's retreat. As the
battle continues additional Astral blocks appear as fall hazards. Later
moving Feywild river blocks begin flowing through the arena. Eventually
it becomes impossible to avoid both the Astral hazards and the River
hazards.

The intended solution is for the player to deliberately jump into a
Feywild river block to avoid an unavoidable Astral Sea block.

------------------------------------------------------------------------

# 6. River Cutscene

Entering a Feywild river block begins a cutscene. Chuck falls into the
tear between worlds into a river and is swept away by the current. The
river runs through the lush Feywild; Chuck passes over a small
waterfall, the river calms, and eventually he washes ashore in the
Feywild. Gameplay ends.

The cutscene uses the same fall-to-Chult / fall-to-Hell soundtrack.

------------------------------------------------------------------------

# 7. Story Notes

Continue reinforcing that the trio are among the people attempting to
repair the collided worlds. Chuck remains an observer moving through
larger events. Do not fully reveal the mystery.

------------------------------------------------------------------------

# 8. Music

The Phlegethos soundtrack is not complete and should be composed during
this phase. Its identity should feel dangerous, adventurous, and
constantly in motion rather than hopeless or mournful. Reference point:
the energy and atmosphere of the Island Lava Caves area from Stardew
Valley -- driving rhythm, mysterious volcanic atmosphere, a sense that
the environment itself is alive. Do not imitate it directly; capture
similar emotional qualities while remaining consistent with CHUCK's
original retro soundtrack identity.

The track should feel: dangerous, adventurous, mysterious, infernal,
energetic, rhythmically driven. Avoid: melancholic, slow, depressing,
ambient-only, hopeless. Hell is an active, hostile place, not quiet
despair.

Favor: heavy percussion, tribal/infernal tom rhythms, driving bass,
metallic hits, eerie melodic leads, pulsing low synths, occasional
choir-like textures. The groove should encourage forward movement.

**Dynamic finale.** During the Pit Fiend encounter, keep the same core
theme but increase intensity with additional percussion and harmonic
tension. When Chuck enters the flowing Feywild river block, transition
into a brief cutscene cue that gradually sheds the infernal
instrumentation before resolving into the usual fall music.

------------------------------------------------------------------------

# 9. Ending Cutscene

Implemented during Phase 8. Reuse the visual language of the descent
into Chult and the fall into the Nine Hells while giving it its own
identity.

1. Chuck deliberately jumps into a flowing Feywild river block to avoid
   an unavoidable Astral Sea hazard.
2. The instant he enters the water, the infernal battlefield disappears
   beneath him.
3. Chuck is carried rapidly downstream through a rushing river suspended
   between colliding worlds.
4. Around the river, lush Feywild vegetation begins appearing along the
   banks.
5. Basalt cliffs gradually give way to moss-covered stone, flowers,
   oversized roots, and vibrant trees.
6. Chuck passes over a short waterfall.
7. The current slows.
8. Chuck gently washes onto a quiet riverbank in the Feywild.
9. The camera lingers briefly on the peaceful contrast before fading to
   black.

The transition should feel like narrowly escaping disaster rather than
peacefully drifting away. The player should clearly understand that
Chuck has survived because the Feywild itself has broken into Hell as
the worlds continue to collide.

------------------------------------------------------------------------

# 10. Out of Scope

Do not implement: Feywild gameplay, Pit Fiend defeat, river-exploration
gameplay, an explanation of the flowing Feywild river, or an explanation
of the collided worlds.

------------------------------------------------------------------------

# 11. Acceptance Criteria

- [x] Multiple connected Phlegethos maps are implemented. *(five)*
- [x] Basalt, lava, statues and fortress exteriors establish the setting.
- [x] Lemures reuse zombie gameplay.
- [x] Fire snakes reuse temple-snake gameplay.
- [x] Spined devils create ranged dodge hazards and instantly defeat
  Chuck in melee.
- [x] Flameskulls weave rapidly as hazards.
- [x] Horned devils reuse the large-dinosaur gameplay.
- [x] Lava traversal and jump sequences are complete. *(the authored
  lava-lake island crossing supplies the phase's traversal set piece)*
- [x] Fortress climax functions.
- [x] Trio battles the Pit Fiend.
- [x] Dialogue reinforces the trio's mission.
- [x] Astral Sea hazards escalate.
- [x] Feywild river blocks become the only escape.
- [x] Chuck washes ashore in the Feywild.
- [ ] Phase 9 begins there.

------------------------------------------------------------------------

# Implementation Log

(Slices are appended here as they land, newest last.)
