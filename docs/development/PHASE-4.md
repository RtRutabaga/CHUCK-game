# PHASE 4 — CHULT JUNGLE

## Status

Phase 3 is complete, including the falling and landing cutscene into Chult.
Phase 4 begins with Chuck already in the first playable Chult area.

This phase establishes Chult as the game's first substantial region after
Waterdeep and begins expanding the exploration structure beyond the opening
tutorial. The playable maps must continue directly from the completed
cutscene, which is the primary reference for Chult's palette, vegetation, sky,
terrain, atmosphere, and graphical language.

## Phase Goal

By the end of Phase 4, the player should be able to:

1. Complete the fall from the Phase 3 cutscene.
2. Land in the Chultan jungle and regain control of Chuck.
3. Activate the first Chult ashtray/checkpoint.
4. Explore a compact jungle area.
5. Learn how Chult's vegetation, terrain, and wildlife affect movement.
6. Encounter a route that depends on Chuck's small size.
7. Encounter simple Chultan wildlife or enemies using existing combat.
8. Discover evidence that other travelers passed through the jungle.
9. Reach the next route deeper into Chult.

Phase 4 establishes the visual, technical, and gameplay language for future
Chult maps. Do not attempt to build the entire region in one phase.

# 1. First Chult Map

Create the first playable Chult jungle map. Translate the completed cutscene's
palette, vegetation shapes, terrain language, atmosphere, and graphical
simplicity into normal top-down gameplay. Do not redesign Chult independently.

The map should be larger and more exploratory than the Phase 2 sewer while
remaining contained enough to build and polish as one area. It should have a
clear overall route with small opportunities to wander, not a huge open world.

Primary visual materials may include jungle ground, mud, wet stone, dense
grass, broad leaves, vines, roots, trees, fallen logs, small pools or water,
and canyon or raised-stone boundaries. Keep graphics simple and readable at
the native 320×180 resolution.

The first map should contain the landing area, first Chult ashtray, main route,
an optional side path, one Chuck-sized route or shortcut, one simple
wildlife/combat section, evidence of previous travelers, and a transition
toward the next Chult area. The player should understand it through exploration
rather than a minimap or quest marker.

# 2. First Chult Ashtray/Checkpoint

Place the first Chult ashtray near the beginning, shortly after control returns.
Use the existing checkpoint and save architecture. Activating it must set the
active checkpoint, save required progression, become the Sanity-zero respawn
point, and allow CONTINUE to restore the correct Chult state.

Recommended display name: `Chult 1`. Use the project's checkpoint-ID convention.

# 3. Chult Exploration Language

Jungle obstacles should arise primarily through terrain and scale: roots,
thick grass, obscuring leaves, shallow water or mud, logs, rock gaps, animal
tracks, vines, and oversized discarded expedition objects. Reuse movement,
jumping, collision, interaction, and hazard systems where possible.

Include at least one route that exists because Chuck is approximately one foot
tall—for example beneath a log or crate, between roots, or through a small rock
opening. It may be a main route, shortcut, or optional discovery. Do not add a
crouch button unless technically necessary; if Chuck fits, he simply moves
through it.

# 4. Zombies, Skeletons, and Combat

The primary enemies in the first Chult maps are zombies and skeletons. Use the
existing human-NPC scale and simple procedural pixel-art style. They can be
defeated with Chuck's scratch attack but should require many scratches, making
avoidance or escape practical and often preferable. Do not require clearing
every enemy to progress.

Keep behavior readable: slow direct pursuit for zombies and, only if it fits
the existing architecture cleanly, a modestly different speed or pattern for
skeletons. Do not add weapons, equipment, upgrades, damage numbers, or a skill
tree. Test collision, pursuit, Sanity damage, scratch hit detection, repeated
damage, defeat, escape, death, and checkpoint respawn.

# 5. Environmental Hazard

Add one simple, readable, reusable Chult terrain problem: deep mud that slows
Chuck, thorny vegetation that damages Sanity, a dangerous plant with a simple
reach area, a narrow water crossing, or unstable ground. Choose one. Do not
implement several new terrain systems in the same phase.

# 6. Evidence of Previous Travelers

Include a small environmental scene such as an abandoned camp, damaged
raincatcher, large backpack, broken canoe fragment, discarded map, boot,
extinguished fire, large tool, or torn expedition cloth. Chuck's scale should
affect how it reads; a backpack can be architectural and a boot can be a large
object. One or two objects may use very brief text such as `Empty.`,
`Still wet.`, `Too large.`, or `Someone left quickly.` Do not add a lore dump.

# 7. Campaign References

Phase 4 may use Tomb of Annihilation history as restrained environmental source
material. Do not place the original party as active NPCs or recreate the recap
as the main plot. Verify any specific reference against
`Tomb-of-Annihilation-Campaign-Notes.txt`; do not invent campaign history. Use
no more than one overt reference unless Sean approves more.

# 8. Chult Music and Ambience

The Chult soundtrack needs to **SLAP**. Create an original, memorable,
jungle-oriented exploration theme consistent with CHUCK's retro/procedural
sound language. Use 16-bit Donkey Kong Country only as a broad reference for
groove, atmosphere, low-end presence, and confidence—never copy its melodies,
bass lines, or arrangements.

Emphasize deep bass, a strong bass line, syncopated jungle percussion, layered
groove, humid atmosphere, and a clear melodic identity. Do not make it quiet
generic ambience or modern cinematic orchestral jungle music. Stylized insects,
distant birds, water, rain, dripping vegetation, or animal calls may sit
underneath, but the music remains the main audio identity.

# 9. Chult Map Exit

Lead to a clear route deeper into the jungle: a trail, canyon passage, river
route, or vegetation opening. If the next full map belongs to Phase 5, Phase 4
may stop at a stable transition boundary. Do not build Port Nyanzaru without an
explicit scope change.

# 10. Save and Development Checkpoints

Integrate Phase 4 with the shared checkpoint architecture. Define at least
`Chult 1`, and make the development selector load it through the same checkpoint
loader as player saves. It must initialize enough state to work without
replaying Waterdeep, sewer, tavern, pantry, or the fall. Do not create a
separate debug teleport. A meaningful second boundary may be named `Chult 2`.

# 11. State and Progression

Use only the state needed for this area, potentially fall completed, Chult
reached, Chult 1 activated, a shortcut opened, or one-time interactions. Do not
build a quest system, inventory progression, equipment progression, or a
permanent power upgrade.

# 12. Art Requirements

Phase 4 art may include jungle ground, mud, wet stone, water, broad leaves,
dense grass, vines, roots, trees, logs, flowers, the Chult ashtray environment,
expedition debris, one hazard, one wildlife/enemy type, and landing elements.
Match the simple procedural pixel-art presentation and use the Phase 3 cutscene
as the primary Chult reference. Maintain native 320×180 rendering and prioritize
silhouettes and composition over detail.

# 13. Architecture

Reuse established maps/scenes, entities, NPCs, interaction, collision, jumping,
combat, damage/Sanity, hazards, checkpoints, saves, camera, and audio. Add a
system only when required by the selected hazard or wildlife. Keep Chult content
separate from Waterdeep/sewer-specific rendering where practical. Do not put
the entire implementation in `main.py` or broadly rewrite completed systems.

# 14. Out of Scope

Do not implement the full Chult region, Port Nyanzaru, the full Tomb plot, the
Death Curse, Soulmonger, Omu, Tomb of the Nine Gods, guide selection, dinosaur
racing, full survival simulation, hunger, thirst, crafting, equipment
progression, a large inventory or enemy roster, boss fights, procedural jungle
generation, or world-map fast travel.

Phase 4 is focused on **the Chult arrival, first checkpoint, first jungle map,
basic Chult exploration language, one simple wildlife encounter, one
environmental hazard, and a route deeper into the jungle.**

# 15. Acceptance Criteria

## First Chult Map

- [ ] Tropical jungle reads clearly at native scale.
- [ ] The map is larger and less linear than the sewer, with a readable main
  route and optional side path.
- [ ] Collision and camera bounds are stable.
- [ ] Chuck's small size remains visually clear.

## Ashtray and Save

- [ ] Chult 1 appears near the beginning, activates, saves, and becomes the
  Sanity-zero respawn point.
- [ ] CONTINUE restores the correct Chult state.

## Exploration

- [ ] A readable Chuck-sized route or shortcut exists.
- [ ] Jungle terrain creates meaningful geometry without a quest marker or
  minimap requirement.

## Zombies, Skeletons, and Combat

- [ ] Human-scale zombies and skeletons match the visual style.
- [ ] Existing scratch combat, repeated damage, enemy defeat, collision, and
  Sanity damage work correctly.
- [ ] Avoidance is realistic and clearing every enemy is not mandatory.
- [ ] Checkpoint respawn works after an encounter death.

## Environmental Hazard

- [ ] One readable and consistent Chult-specific hazard or terrain mechanic is
  implemented in a reusable form.

## Environmental Storytelling

- [ ] Evidence of previous travelers reads at gameplay scale and uses a
  human-scale object to reinforce Chuck's size.
- [ ] There is no exposition dump and no more than one overt campaign reference.

## Audio

- [ ] Chult has a strong original jungle theme with deep bass, memorable bass
  line, syncopated percussion, layered groove, and CHUCK's retro identity.
- [ ] Ambience stays secondary; audio remains stable after death and respawn.

## Technical Quality

- [ ] Clean-start play works through Chult arrival; NEW GAME and CONTINUE work.
- [ ] The development selector loads Chult 1 through the shared loader.
- [ ] Waterdeep, sewer, tavern, and pantry still work.
- [ ] Scene transitions do not duplicate or lose Chuck.
- [ ] Existing tests pass and targeted regression tests exist where practical.

# 16. Final Playtest

Test both routes.

For the full route, play Waterdeep → sewer → Waterdeep return → tavern → pantry
→ fall → Chult arrival → Chult 1 → first jungle area → wildlife encounter →
first map exit.

Also load `Chult 1` directly through the development selector. Verify the fall
resolves cleanly, Chult reads as a distinct region, the map is more exploratory
than the sewer, its routes are readable, a side path rewards inspection, scale
creates a route, combat works, the selected hazard is consistent, the traveler
scene belongs in the world, saving/respawn work, direct loading initializes the
area, and the route deeper is clear.

Phase 4 is complete when Chuck has landed, activated Chult 1, explored the first
jungle area, encountered the region's basic gameplay language, and reached the
route deeper into Chult.
