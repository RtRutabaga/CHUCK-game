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

- [ ] Multiple connected Phlegethos maps are implemented.
- [ ] Basalt, lava, statues and fortress exteriors establish the setting.
- [ ] Lemures reuse zombie gameplay.
- [ ] Fire snakes reuse temple-snake gameplay.
- [ ] Spined devils create ranged dodge hazards and instantly defeat
  Chuck in melee.
- [ ] Flameskulls weave rapidly as hazards.
- [ ] Horned devils reuse the large-dinosaur gameplay.
- [ ] Lava traversal and jump sequences are complete.
- [ ] Fortress climax functions.
- [ ] Trio battles the Pit Fiend.
- [ ] Dialogue reinforces the trio's mission.
- [ ] Astral Sea hazards escalate.
- [ ] Feywild river blocks become the only escape.
- [ ] Chuck washes ashore in the Feywild.
- [ ] Phase 9 begins there.

------------------------------------------------------------------------

# Implementation Log

(Slices are appended here as they land, newest last.)
