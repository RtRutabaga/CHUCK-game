# PHASE 12 --- THE CABIN

## Status

Phase 11 is complete. Chuck has crossed the oval planar portal in the final
rainy-city map and the existing transition records
`doug_fir_transition_completed` after showing him emerge from a Douglas fir at
night.

Phase 12 begins with Chuck in the Douglas-fir forest at the mysterious Cabin in
Washington. This phase is based on a real place. The authored map and
photographs in `docs/design/references/tahuya-cabin/` are primary visual and
spatial references and must be followed closely.

This phase contains exactly two playable maps:

1. the cabin grounds, including both accessible covered porches
2. the cabin interior

There are no enemies and no environmental hazards in this phase. Its tension
comes from faithful place, unusual light, strange occupants, and the gradual
change in the D&D map on the long west-wall table.

------------------------------------------------------------------------

## Phase Goal

By the end of Phase 12, the player should:

1. Regain control in the Douglas-fir forest outside the Cabin.
2. Explore the clearing and both accessible porches.
3. Enter and leave the cabin through either the front or back door.
4. Recognize that the playable interior fits within the exterior cabin shell.
5. Meet four light-formed entities seated in the cabin.
6. Hear each entity's unique, unaltered strange dialogue.
7. Speak with all four entities.
8. Cross the back door after all four conversations.
9. Return to or remain in the interior and discover that the rectangular D&D
   map on the long west-wall table has become a planar surface.
10. Confirm entry through that surface and see Chuck arrive in a desert.

The desert arrival is the stable boundary for the following phase. Do not
build desert gameplay during Phase 12.

------------------------------------------------------------------------

# 1. Reference Authority and Fidelity

Use the references in this order:

1. Sean's current direct instructions
2. `docs/design/references/tahuya-cabin/authored-map-layout.jpeg` for relative
   spatial layout
3. the cabin photographs for structure, materials, palette, furniture, and
   scale
4. `color-changing-mushroom-lights.jpg` for the outdoor lights
5. established CHUCK procedural pixel-art and native-scale rules

The photographed property is not loose inspiration. Preserve the authored
relationship among the cabin, porches, stairs, doors, forest paths, firepit,
outbuilding/firewood shed, marked lights, large outdoor features, and interior
furniture.

The hand drawing is schematic and not a literal tile grid. Translate it into
stable collision and readable top-down movement without rearranging the place
into a more conventional videogame layout. If a detail is genuinely unclear,
stop and ask Sean rather than inventing a materially different feature.

------------------------------------------------------------------------

# 2. Outdoor Cabin Map

Create one larger nighttime Douglas-fir forest map around the cabin.

The cabin must use a three-quarter top-down view with visible wall faces and a
visible roof. It should read as a small, aging blue-gray forest cabin with:

- a shallow gabled, moss-weathered roof
- broad overhangs
- a raised foundation
- weathered siding
- covered front and back porches
- porch posts and lattice
- human-scale stairs
- dense evergreen forest and understory close around the clearing

Both porches are playable parts of the outdoor map. Their stairs, floorboards,
rails, posts, and door approaches must be readable at native scale. Neither
porch is a decorative inaccessible facade.

The exterior cabin shell and roof must be large enough to contain the complete
interior footprint at the same implied scale. The interior may use cleaner
walls for gameplay readability, but it must not be wider or deeper than the
roofed cabin visible outdoors.

## Grounds Layout

Follow the authored layout, including:

- the cabin and its two porches on the right side of the grounds
- the front and back stair approaches
- the winding forest edge/path language
- the marked firepit area
- the marked firewood shed/outbuilding
- the circular feature labeled `UFO`
- the large rocks and other major drawn ground features
- the small circles marking the color-changing lights

Do not add combat arenas, jump challenges, fall tiles, damaging plants, or
other gameplay pressure. The map is a quiet place to inspect.

## Outdoor Checkpoint

The outdoor map receives exactly one physical Ashtray and one development
checkpoint through the shared checkpoint loader. It must be safe and should
not obscure a reference landmark.

Recommended display name:

> Cabin Exterior

Use the project's actual checkpoint-ID conventions during implementation.

------------------------------------------------------------------------

# 3. Color-Changing Mushroom Lights

Place the small garden/path lights at the circles marked `RGB` on the authored
layout. Their physical form is the short mushroom-like solar light shown in
`color-changing-mushroom-lights.jpg`.

The lights cycle through more than simple red, green, and blue. Their animated
palette should include a smooth sequence such as:

- rose/pink
- violet
- blue
- cyan
- green
- yellow
- warm amber

Each light sheds a restrained pool of colored light onto the nearby ground,
using the projected-light language established by the City Day 6 planar
portal. The glow must remain readable at native scale without whitening the
whole clearing.

All lights use the same color cycle but different authored phase offsets.
They must visibly show different colors at the same moment and must not drift
back into synchronized animation after a map transition or checkpoint load.
Use a deterministic offset per placed light rather than randomizing their
state each frame.

------------------------------------------------------------------------

# 4. Cabin Doors and Map Relationship

The front and back doors both connect the outdoor and indoor maps through the
established area-transition system.

- Entering the front door places Chuck at the matching front-door interior
  arrival.
- Leaving through the front door places him on the matching front porch.
- Entering the back door places him at the matching back-door interior
  arrival.
- Leaving through the back door places him on the matching back porch.

Every visible threshold must line up with its real collision/transition tile.
Do not place arrivals several tiles away from the depicted doorway.

These are ordinary cabin thresholds, not YES/NO interactions. Music should
continue uninterrupted between the grounds and interior because they are one
setting.

------------------------------------------------------------------------

# 5. Cabin Interior Map

Create one compact top-down interior matching the authored drawing and photo
references. It must fit inside the outdoor cabin's roofed footprint.

Use the photographs' warm, aged interior language:

- dark brown vertical wood paneling
- exposed beams and low ceiling character
- warm, localized incandescent light
- muted tan/olive carpet and worn floor surfaces
- human-scale furniture that reinforces Chuck's one-foot height
- dark wood cabinets and counters
- a freestanding wood stove/fireplace and black stove pipe

Preserve the authored relative placement of:

- big couch
- second couch
- the doorway between the couches
- two separate chairs along the right side
- long table and stools against the west wall near the big couch
- counter and sink/kitchen run
- rectangular D&D map on the long west-wall table
- fireplace/wood stove area
- full closed southeast room
- front door and back door

Furniture should create believable level geometry without making the small
room frustrating to navigate. Chuck must be able to reach all four entities,
both doors, and the table map.

## Interior Checkpoint

The interior receives exactly one physical Ashtray and one development
checkpoint through the shared loader.

Recommended display name:

> Cabin Interior

The checkpoint must restore all four conversation flags and the correct normal
or awakened state of the table map.

------------------------------------------------------------------------

# 6. The Four Entities

Place exactly four seated NPCs:

1. one on the big couch
2. one on the second couch
3. one in the first chair
4. one in the second chair

They are not ordinary humans. Each entity is a readable seated humanoid
silhouette formed from the same smooth, changing gray/tie-dye light language
as the City Day 6 planar portal. Their colors may travel across their bodies
and cast subtle local light, but their silhouettes must remain legible against
the warm brown room.

Offset their animation phases so the four entities do not change color in
sync. They remain stationary, non-hostile, and non-colliding beyond ordinary
NPC interaction spacing.

Each entity has one unique exact dialogue. Preserve the source strings byte
for byte where practical and do not normalize, translate, correct, or replace
their unusual characters:

> ꋖꁝꌅꊿꁲꋖꊿꂵꑀ ꃳꁲꏳꈵ

> i̵̖s̵̻̆͗i͙͢t̞ꁲꃔꏳh̵̨i̲͖̣͋c̘̆ͬḩ̜̣͙t̝ͬͣi̽?

> l̛͠ơ̶̧͟g̸̶̀͘c҉a͢b͏̸̵̴̵į̷̴̕͜n͘҉ í̸s̵̡͜͏͟͢ t̶̡́͡͡͡h͏̡̕o̸͜͞ņ̶̸̸̴͟l̶̷̨͘y͢͠҉̧w̢̕͜͜à̵́͡͝y҉

> į̷̴̕͜n͘҉ í̸s̵̡͜͏͟͢ꋖꊿl̶̷̨͘y͢͠҉̧w̢̕͜͜t̝ͬͣ

The dialogue renderer must visibly preserve the intended strange glyphs. If
the current pixel font lacks them, use a contained fallback or pre-rendered
glyph treatment rather than silently displaying empty boxes or question
marks. Do not replace the dialogue with ordinary English.

Speaking to an entity sets one durable progression flag. Repeated interaction
may replay that entity's same line; it must not duplicate progression.

------------------------------------------------------------------------

# 7. Table Map Awakening

The cabin begins with an ordinary rectangular D&D map lying on the long table
against the west wall near the big couch.
It is readable as a human-scale tabletop object and occupies a fixed rectangle
on the table.

The awakening condition is:

1. Chuck has spoken with all four entities.
2. Chuck then crosses the back-door transition.

The first back-door crossing after all four conversations sets one durable
`table map awakened` state. Do not activate it merely after the fourth
conversation, and do not require a particular order for the four entities.

When the interior is next visible—including immediately if the qualifying
back-door crossing enters the interior—the D&D map has transformed. It remains
the same rectangular size and position on the table, but its surface now
uses the smooth gray, swirling tie-dye animation and projected-light language
of the City Day 6 portal. It does not become a freestanding oval.

The awakened state persists through either door, Sanity/checkpoint loading,
CONTINUE, and development-checkpoint loading with the required flags.

------------------------------------------------------------------------

# 8. Desert Portal Interaction and Cutscene

The ordinary D&D map has no planar interaction. Only its awakened state can
prompt the player.

Approaching closely displays:

> Enter planar portal?

Options:

- `YES`
- `NO`

Selecting `NO` closes the dialogue with no additional text.

Selecting `YES` begins a short, input-locked transition cutscene showing Chuck
arrive in a desert. Use the established scene and fade architecture rather
than loading a separate debug destination.

The cutscene should establish only the desert arrival needed for the next
phase. Do not create desert exploration, enemies, NPCs, hazards, narrative, or
an invented desert map in Phase 12. End at a stable handoff state that the next
phase can resume authoritatively.

------------------------------------------------------------------------

# 9. Progression and Save State

Persist only the minimum state required to restore the phase reliably:

- Douglas-fir transition completed / Cabin reached
- current active cabin checkpoint
- one conversation flag for each of the four entities
- table map awakened
- desert transition completed, once the cutscene finishes
- current Sanity and existing shared player state as already supported

The `all four spoken` condition should be derived from the four individual
flags rather than stored as a second contradictory truth.

Both production saves and development checkpoints must use the shared
checkpoint loader. Do not create a cabin-only debug teleport or a parallel
save format.

------------------------------------------------------------------------

# 10. Music

This phase's music is a major feature and should receive a dedicated,
separately reviewed implementation pass.

Compose one original Cabin theme shared by the outdoor and indoor maps.
It should continue uninterrupted through both doors.

The target character is:

- strange and psychedelic
- catchy rather than formless
- driven by a memorable bass line
- rhythmically confident
- warm enough to coexist with a familiar cabin
- subtly uncanny as the entities and table map reveal themselves
- enriched by Indian-inspired hand-drum colors, such as tabla-like tuned
  strokes, without directly copying a traditional composition
- consistent with CHUCK's established procedural/retro soundtrack language

Shpongle is a broad reference for psychedelic layering, organic/electronic
mixture, and playful strangeness only. Do not copy any melody, bass line,
rhythm, arrangement, sample, or production signature from an existing track.

The arrangement should build with care. Keep the bass hook clear as layers
enter, avoid the clutter and dissonant peak previously corrected in the
Feywild theme, and preserve a strong loop seam. The result should feel like a
complete area theme, not generic forest ambience.

Environmental audio may include restrained night forest, distant wind in firs,
porch creaks, fire, and interior room tone. Ambience remains secondary to the
music.

------------------------------------------------------------------------

# 11. Architecture

Reuse established systems for:

- procedural 320x180 pixel art
- maps, markers, camera bounds, and collision
- reversible named arrivals
- ordinary door transitions
- NPC interaction and dialogue
- deterministic animated props
- projected colored light
- progression flags and save serialization
- shared checkpoints and Sanity-zero respawn
- YES/NO choice scenes
- cutscene fades and stable phase handoffs
- uninterrupted same-region music

Keep cabin-specific content in dedicated map, art, entity, and cutscene modules
where practical. Do not place the phase implementation directly into
`main.py`, duplicate the City Day 6 portal system wholesale, or introduce a
modern UI framework.

------------------------------------------------------------------------

# 12. Out of Scope

Do not implement during Phase 12:

- enemies
- combat encounters
- damaging or slowing terrain
- jump or fall-hazard challenges
- additional forest maps
- additional cabin rooms or floors not shown in the authored layout
- dialogue beyond the four exact entity strings and the portal prompt
- an explanation of the entities
- an explanation of why this real cabin exists between worlds
- desert gameplay
- desert NPCs, enemies, hazards, or story
- inventory, equipment, quests, or permanent upgrades

Phase 12 is focused on faithful place, quiet exploration, strange occupants,
the table-map transformation, its music, and the desert handoff.

------------------------------------------------------------------------

# 13. Acceptance Criteria

## References and Layout

- [x] All nine authored reference files remain in
      `docs/design/references/tahuya-cabin/`.
- [ ] The outdoor and indoor maps closely follow the authored map layout.
- [ ] The cabin is three-quarter view with visible walls and roof.
- [ ] The complete interior fits within the exterior roofed footprint.
- [x] Both porches are accessible.
- [ ] Both doors align visually and transition reversibly.
- [x] No enemies or hazards are present.

## Exterior

- [x] The clearing reads as a Douglas-fir forest at night.
- [ ] Cabin siding, mossed shallow roof, raised foundation, porch structure,
      lattice, stairs, and dense understory match the references.
- [ ] Firepit, shed/outbuilding, circular `UFO` feature, large rocks, paths,
      and marked light positions follow the drawing.
- [x] Color-changing mushroom lights use multiple colors and cast local light.
- [x] The lights use stable offsets and are visibly unsynchronized.
- [x] The exterior has one physical Ashtray and one shared-loader checkpoint.

## Interior

- [ ] Paneling, palette, lighting, stove, furniture scale, and kitchen language
      match the photographs.
- [ ] Both couches, both chairs, west-wall table/stools, counter/sink, fireplace,
      closed southeast room, doors, and rectangular D&D map are present in their
      authored relationship.
- [ ] The interior has one physical Ashtray and one shared-loader checkpoint.
- [ ] Navigation reaches every entity, both doors, and the table map.

## Entities and Progression

- [ ] Exactly four seated light entities occupy the two couches and two chairs.
- [ ] Their animation phases are offset.
- [ ] Each displays its exact unique strange dialogue legibly.
- [ ] Each conversation sets one durable flag and repeats safely.
- [ ] The D&D map remains ordinary until all four entities have been spoken to
      and Chuck subsequently crosses the back door.
- [ ] The awakened map retains the original rectangular footprint and table
      position while gaining gray tie-dye motion and projected light.
- [ ] Save, CONTINUE, respawn, and development loading restore the correct
      conversation and portal state.

## Portal and Boundary

- [ ] Only the awakened map displays `Enter planar portal?` at close range.
- [ ] `NO` closes silently.
- [ ] `YES` starts the desert-arrival cutscene.
- [ ] The cutscene ends at a stable Phase 13 handoff without desert gameplay.

## Audio and Technical Quality

- [x] The original cabin theme is catchy, cool, bass-driven, and uses a driving
      retro-techno beat, an exciting synth melody, and restrained
      Indian-inspired hand percussion.
- [x] The peak arrangement remains coherent rather than cluttered.
- [x] Music continues uninterrupted between exterior and interior.
- [ ] Both maps render at native 320x180 and preserve Chuck's one-foot scale.
- [ ] Both maps load through the shared development checkpoint selector.
- [ ] Sanity-zero respawn uses the active cabin Ashtray.
- [ ] Existing tests pass and targeted Phase 12 tests are added where practical.

------------------------------------------------------------------------

# 14. Final Playtest

## Production Route

1. Continue from the completed City Day 6 portal state.
2. Verify the Douglas-fir transition hands off cleanly to the cabin exterior.
3. Explore the grounds, both porches, and reference landmarks.
4. Enter through the front door and return outside through it.
5. Enter through the back door and verify the matching arrival.
6. Speak with all four entities and verify each exact line.
7. Confirm the table map has not awakened before the required back-door
   crossing.
8. Cross the back door after all four conversations.
9. Return to or remain in the interior and inspect the awakened rectangular
   table portal.
10. Choose `NO` and verify the dialogue closes silently.
11. Choose `YES` and verify the desert-arrival cutscene and stable handoff.

## Development Checkpoints

Load both cabin checkpoints directly through the shared selector.

Check:

1. Does the exterior preserve the authored layout rather than merely evoke a
   generic cabin?
2. Are both porches genuinely walkable and both doors aligned?
3. Does the interior plausibly fit within the visible exterior shell?
4. Do the furniture and architecture make Chuck look one foot tall?
5. Are the mushroom lights unsynchronized and casting restrained colored light?
6. Are all four entity strings legible and unchanged?
7. Is the back-door crossing, not the fourth conversation alone, what awakens
   the table map?
8. Does reloading preserve every state without replay or duplication?
9. Does the music remain catchy and clear at its fullest arrangement?

Phase 12 is complete when the faithful two-map Cabin can be explored,
all four entities can be met, the back-door condition awakens the table map,
and Chuck can choose the planar surface to reach the desert handoff.
