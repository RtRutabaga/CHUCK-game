# CHUCK — Project Status

Updated: Phases 12, 13, and 14 are feature-complete. Waterdeep now supports its
quiet opening and populated midday finale on shared city geography.
The Collided Desert's five-map opening region is complete and has had a second art pass --
hub, orc camp, oasis and undead ruins, now with fissured cliffs, fallen
columns, palm trees and axe-carrying orcs -- and the eastward traversal runs
six maps deep, through the modern city, Chult, the Feywild, the Nine Hells, a
ship's deck, a crenellated castle flying its own colours and a frozen
world with a blue dragon in it, then a
seventh map where nine worlds meet and none of them owns the ground, and an
eighth where the ground has mostly gone and what is left is islands in the
Astral Sea. The walk ends at the trio: they are on their map, working on the
rift, the whole scripted conversation plays across the fight while the rift
takes the arena a column at a time, the desert is overwhelmed by fragments of
everywhere as they close it, and the last thing the wizard says sends Chuck
home. Through the last of it a horde of orcs presses the two heroes who are
fighting, the Astral closes in from the west until the only place left to
stand is the fight itself, and a red dragon crosses the arena laying fire
behind it -- coming down between crossings to spit rolling fire that gets
faster than Chuck is. The phase runs from the cabin table to the Waterdeep
docks, on
one unbroken piece of desert music that becomes a mashup with the fall to
Chult for the climax and a boss theme when the dragon arrives. This file
is required by the project rules
and updated every session.

## Latest implementation

### Chult Falls: a tortle by the chest

- **The tortle** stands just east of the Falls' chest, on the west bank. His sprite is `npcs/tortle.png`, made by `tools/generate_tortle_sprite.py` from the user's reference: an old, hunched turtle-man, green and beaked, with a pale plastron, a plated brown shell with moss on top, a blue vest, brown trousers and a knobbly walking stick. Like every standing NPC he has down, up and left frames, and faces Chuck when spoken to.
- **Wider sheet:** his frames are 24px wide instead of 16 because of the shell. The standing NPC reads per-NPC frame widths from `NPC_FRAME_WIDTHS` in `src/entities/npc.py`, and his interaction zone widens to match.
- **Dialogue** (`data/dialogue/chult.json`): "Piss off!" the first time, then "I said scram!" every time after. This uses the existing `_repeat` second-word mechanism.
- **Map marker:** `Ꝡ` (`npc:tortle`), placed by `tools/generate_chult_falls.py` at (15,22).
- **Tests:** a new test in `tests/test_chult_falls.py` covers his placement by the chest, the wide frames and interaction bounds, and the first line then the repeat line.
### Chult Falls: a hidden waterfall map off Chult 4

- **Hidden way in.** Chult 4's western side pocket (row 30) now runs through the west wall. Cols 0-2 are walkable trail drawn over with the same dense-jungle overhead art as the wall (`ꝏ` exit, `Ꝓ` passage), so the wall looks unbroken until Chuck steps in and the canopy thins over him. The only tell is one trail tile at the mouth, (3,30). Coming back, Chuck arrives at (4,30), facing right (`Ꝕ`).
- **Chult Falls** (`assets/maps/chult_falls.txt`, 48x40, made by `tools/generate_chult_falls.py`), set up like the Lost waterfall reference:
  - **Cliff and fall:** a dark basalt cliff across the north, with moss, ferns, vines and jungle down its sides. The fall is animated in 4 frames, with mist and spray (`Ꝙ`, prop `chult_falls`; art by `tools/generate_chult_falls_art.py`).
  - **Pool:** turquoise, with round mossy boulders on the shore (`Ꝛ`) and in the water (`Ꝝ`).
  - **River:** one tile wide, runs south from the pool to the map's bottom edge. It is Chult 4's own `≈` stream tile.
  - **Way in and out:** Chuck arrives on the east bank. The exit back is the jungle arch (`ð`) on the east edge.
- **Chest:** `Ꝟ`, kind `chult_falls_chest`, on the west bank. It can only be reached by jumping the river.
  - It is the ruin chest's twin, with its own flags (`chult_falls_chest_opened`, `chult_falls_chest_carton_collected`) and its own carton of premium Buhetian halfling leaf.
  - The world scene now builds its flags from the kind.
- **Wiring:**
  - Checkpoints `chult_falls` (in the dev selector) and `chult_4_from_falls` (runtime only).
  - Chult tileset and chult.wav.
  - Examine lines for the falls, the boulders and the chest (closed and open).
- **Tests:**
  - New file `tests/test_chult_falls.py` covers:
    - the hidden entrance art and that it can be reached
    - exits both ways
    - the river running unbroken from the pool to the south edge
    - the chest needing the jump
    - the chest's separate flags and carton
    - the animated falls
  - The dev selector name list in `test_checkpoints.py` gains "Chult Falls".
- The rowboat by Bobert's barrel now lies alongside the pier rather than
  sticking out from it: north-south against the big pier's west edge, bow to
  the north, its bow line running down the pier side to the post beside him
  -- the way a boat is tied up, and the way the opening cutscene shows it,
  parallel to the quay. Redrawn for that orientation rather than rotated: we
  look down into it (planking, thwarts, oars), the bow narrows to a point
  pointing away up the screen, the transom is the one outside face toward us,
  and the long sides show only as gunwale rims.
- The Needle Garden's flowering beds are needles now: Chuck can walk through
  them, and like Chult's thorns they cost him (the same sanity damage, in
  src/systems/terrain_hazard.py, and not while he is in the air). The
  spitting orchids' seeds still stop at the beds (`NEEDLE_BEDS` as extra
  solid terrain for seeds only), so every firing lane is the lane it was, and
  the garden's lane and bypass tests treat a bed as bounding a lane.
- A rowboat is tied up by Bobert's barrel: on the water west of the big pier,
  bow to the west-edge post beside him, the same boat mirrored so its line
  runs east from the bow to the post and its stern points out to sea
  (harbour_rowboat_west, with its midday twin). It is the boat the opening
  cutscene shows by the posts where Chuck wakes, and the opening cutscene's
  street lamp is gone, since there is no lamp on that stretch of dock.
- Only the ways out reach the edge of a city map now. Every day and night city
  map (the arrival, Day 1-6, Night 2-6) was audited for walkable tiles on its
  outer row or column that are not part of a wired exit. Four maps had them:
  Night 5's whole south edge, where both highways and their pavements ran
  straight off the map; one-tile pavement slivers past building corners at
  the top and bottom of Day 3; a tile at the top and two runs at the bottom of
  Night 3; and one at the bottom of Night 4. Each is closed with the Astral
  Sea three tiles deep, like the bands already sealing the cities' other
  dead ends (Night 5's south now matches its north).
- `seal_open_edges` in tools/generate_city_map_common.py does it, run last by
  every day and night generator: any walkable edge tile that is not one of
  the map's AREA_WALK_EXITS characters or an arrival marker inside an exit
  strip, together with plain ground up to three tiles behind it, becomes
  'V'. The generators still reproduce the shipped maps, and a test audits the
  shipped edges.
- New Game opens on a cutscene: Chuck wakes up on the Waterdeep docks beside
  Bobert. The same low quayside vantage as the return-to-Waterdeep cutscene,
  built to rhyme with it -- the mooring posts along the quay edge, the rowboat
  tied up on the water beyond, a lit street lamp -- but in the opening docks'
  evening: the night sheet's planks and navy water with its star flecks,
  under a dusk sky going from indigo to a low warm glow, the first stars and
  a late gull. About seventeen and a half seconds: fade in from black on
  Bobert snoring in his barrel and Chuck curled asleep against it (a new
  two-frame breathing sprite, chuck/chuck_asleep.png, from
  generate_chuck_sprites.py; chuck.png is unchanged), Z's drifting off both
  of them; Chuck twitches, gets up facing us, looks left, looks right, turns
  side-on and lights a cigarette (lighter sfx, flame, then the ember and
  smoke); fade to black. The docks music starts under it and carries into
  the game. Interact skips to the fade.
- The fade hands to a fresh game on the docks, which fades up out of the same
  black. Waterdeep 1 now puts Chuck facing left, the pose the cutscene ends
  on; the fade up is added by the cutscene rather than the checkpoint, so
  development loads and tests are not held in a fade. The two title tests
  that expected New Game to land straight in the world now play the
  cutscene through first.
- The docks lamp that stood in the mouth of the west district-wall gate moved
  one tile north-west, from (21, 11) to (20, 10), beside the gate's pillar; a
  test now keeps lamps out of gate mouths.
- The return-to-Waterdeep cutscene shows the new harbour. From its low
  quayside vantage, four mooring posts (the map's own post sprite) stand
  along the far edge of the planks where the dock meets the water, and the
  midday rowboat lies on the water beyond one of them, its line running down
  from the bow over the edge to the post. The boat's hull is cropped from the
  map sprite, whose own line runs the other way; the cutscene draws the line
  fresh.
- Waterdeep's harbour is dressed, drawn to the camera's vantage (south of
  everything, above it, looking north). The rules, written out in
  tools/generate_waterdeep_harbour.py: tops are seen; south faces are seen
  and north faces never are; east and west faces are edges; anything flat
  against a wall faces us; anything strung between two points sags down the
  screen.
- The piers finally stand above the water. Their edges are derived from the
  map, never authored: water with planks north of it shows the pier's front
  (plank ends, the shade under the deck, a piling, the waterline); water with
  planks west of it shows the deck's shadow; both shows both; a north-west
  corner shows the corner of shade. North and west sides of a pier get
  nothing, because those faces point away from us or along our view.
- Mooring posts on south edges (above the face) and west edges (toward the
  water), never north or east. One rowboat off the west pier, seen from
  above -- inside planking, thwarts, oars, the painted near hull under the
  gunwale, no far hull -- lying against the pier face with its line sagging up
  to the post's foot. Only one: in the finale the docked ship fills the water
  south of the big pier, the sewer outflow climbs the far pier's face, and the
  fisherman casts into the basin.
- Street lamps on the stone (five on the docks, four in the plaza), lit with
  a warm glow in the opening's evening and out at midday. Shop signs hung flat
  to the facade on a short bracket (bread, fish and barrel on the docks'
  houses; anvil and potion beside the plaza's shop doors) and window boxes on
  every house, tavern and shop window. Washing lines strung across the two
  alleys between the north houses at eave height, fading when Chuck is under
  them.
- Kinds with a `_midday` twin swap to it on the return (`midday_variant` in
  prop.py, applied at spawn for the docks and plaza), so pier wood and water
  tints match the midday tileset. tools/waterdeep_harbour_dressing.py applies
  the docks; the plaza's pieces are in its generator. Every solid piece is
  checked against the walkable area. The pier pieces are mute; the rest have
  examine lines. Two old docks tests now read the facade under signs and
  window boxes.
- The fountain plaza's four watch banners hang on the wall now. They were
  stood on the first row of paving and drawn up from there, so their hems
  hung below the wall's foot into the square; they are set in the wall's
  bottom course instead, the gate's own row, so the cloth runs down the wall
  face and ends where the wall does. The paving row they used to block is
  open again.
- The ship's deck grating is bigger: ten tiles by four (160x60) instead of
  seven by three, still centred between the masts and a row lower so it
  clears the cargo at their feet and the fencers above it.
- The fighter has a real sword. The pale bar painted into his sprite is gone
  (a gauntlet in its place); src/entities/sword.py draws a blade with a gold
  crossguard and leather grip at his hand, held upright behind his shield at
  rest and swung in an overhead cut with a pale trail on every stroke his
  battle calls -- in the sanctum, at the fortress and in the collision
  fight. The swing lasts 0.32s, longer than the 0.18s attack flash, so the
  cut is actually seen, and he turns to face what he is cutting: the pit
  fiend at the fortress, whichever orc reached him in the horde.
- The collided desert's knights carry the same sword in the right hand, in
  every facing, and swing it when Chuck comes within 26px (then a 0.9s
  recovery). The swing is presentation: their harm is still the touch, like
  every pursuer on the undead architecture.
- No tutorial hints on the final Waterdeep. The hint line ("Press E to
  interact", scratch, jump, Ashtray) is only created for the opening's
  tutorial maps; once the return-to-Waterdeep flag is set, the docks, tavern
  and pantry show none.
- The exterior deck's bowsprit no longer fades when anyone is near it. It
  hangs out over the sea where nobody can walk under it, so thinning it only
  ever made the ship's prow flicker; it is out of `SEE_THROUGH_PROPS`.
- A hatch grating lies in the middle of the deck, centred between the two
  masts: a thick plank frame round a lattice of crossed battens with the dark
  of the hold showing through each square, seven tiles by three, flat and
  walked over (a floor prop like the captain's rug). It has an examine line
  ("Down through the gaps, the hold smells of bilge and rope.").
- The return-to-Waterdeep cutscene now lands Chuck on the dock he actually
  arrives on. Its quay was drawn as grey cut stone; the fade clears onto the
  plank beside Bobert's barrel, so the quay is now tiled from the midday docks
  sheet's own plank tiles, with variants picked by the map's `art_index` rule
  and a dark lip where the dock drops to the water. His footstep when he looks
  around is the wooden one. The Phase 13 return test that said "nothing warm
  is left" now checks the sky and water for leftover desert warmth and checks
  the quay is the dock's plank colour.
- The new dressing answers E. Forty-one new examine lines in
  data/dialogue/examine.json cover everything added in the dressing pass that
  stands up or is worth a look, written to the same conventions as before:
  things that look breakable and aren't say a scratch won't do it (the cargo
  stack, the captain's desk, the keg rack, the flour sacks, fallen logs, ruin
  fragments, toppled pillars, iron spikes, orc weapon racks), and decoration
  just says what it is, dryly (the notice board's reward for a rat, the OPEN
  sign that's lying, the basket of onions and apples with no cheese). The two
  lantern colours share one line through `EXAMINE_ALIAS`.
- `MUTE_PROPS` now holds only the ground scatter laid down by the dozen --
  ferns, leaf litter, floor cracks, missing slabs, moss, loose temple bones,
  ember cracks, path stones and lily pads -- so E prompts don't appear under
  every other step. The dressing tests now check the rest answer E, and one
  presses E at the tavern keg rack in the running game.
- The modern city gets a little more furniture, kept deliberately minimal
  because its streets were already well dressed. Every street map, day and
  night, gets one bench and one litter bin on the kerb, under the same rule
  and flood check as the lamps. The night maps (and the arrival) also get two
  different neon signs -- BAR, OPEN, 24H, each stuttering now and then -- on a
  building's bottom facade course above plain pavement, and one grate
  breathing steam. The four sewers get two rusted outflow pipes trickling down
  the brick above their walkways and at most one spray-painted tag.
- Placed by `furnish_street` and `furnish_sewer` in
  tools/generate_city_map_common.py, called by every city generator right
  after `dress_street`; all sixteen generators still reproduce their shipped
  maps and a test says so. The night 3 and night 6 prop inventories now allow
  the new kinds.
- Something very large died in the desert hub. A giant ribcage lies in the
  open sand east of the centre: a horned skull on the ground at the west end,
  a half-buried spine, and five thin rib hoops rising out of the sand, one of
  them snapped, shortening toward the tail. Seven solid tiles along the spine;
  it fades when walked behind. It is the only one, and nothing else was added
  to the open sand.
- The orc camp gets its gear: three stitched-hide tents round the edge of the
  beaten ground, two weapon racks of axes and spears by the fires, and a war
  drum with a painted eye in the middle of the camp. No totem. Both maps are
  still reproduced exactly by their generators (`RIBCAGE` in
  generate_desert_central.py; `TENTS`, `RACKS`, `DRUM` in
  generate_desert_orc_camp.py), and the camp's reachability tests are
  unchanged. The oasis is untouched.
- The Feywild's stone paths have lanterns. On the Shifting Hedge, the Twilight
  Crossroads, the Pollen Orchard and the Blooming Path, crooked-post lanterns
  glowing teal or violet stand in the hedge along the north edge of a path,
  at least seven tiles apart, their light breathing slowly; mossy stones lie
  along the path edges (flat, never two side by side). The Moonmoth Fen gets
  bright lily pads on open water and reeds with cattails just off its banks,
  all at least three tiles from any island, bank, channel or moth, so nothing
  near a committed hop looks like somewhere to land.
- tools/feywild_path_dressing.py edits the shipped maps. It never changes
  walkability (lanterns are hedge, stones are path, plants are water) and
  never lands within two tiles of a marker, because a flower toggles its
  target's terrain and a prop drawn there would stay drawn over whatever it
  became. The map generators are untouched, so their puzzle proofs stand.
- Phlegethos has things lying about in it. On the arrival, the lava road, the
  lava lake, the rubble pass and the fractured way: glowing ember cracks
  (flat), vents breathing a slow column of smoke (walked past, animated, drawn
  as a ragged split rather than a ring so they never read as an eye), bone
  heaps and clusters of rusted iron spikes (solid, each kept only if every
  reachable tile stays reachable). Nothing goes within a tile of lava, a
  fissure, the path, a marker or a prop, and the lava lake gets no solid
  pieces at all.
- The fortress approach gets towers and banners instead: two square towers of
  the fortress wall's iron-black brick with ember glints, spiked merlons and
  red-lit slits, and four black-and-ember banners, all on the open row under
  the wall, symmetric about the gate. Its floor stays plain because the
  battle's Astral waves only flood plain basalt. Applied by
  tools/phlegethos_dressing.py; the banners are the castle banner's animation
  in an infernal palette.
- The jungle temple's four big rooms -- entrance hall, skeleton hall, shrine
  and sanctum -- are dressed with damage and leftovers. Cracks run across
  several slabs, beds of earth show where slabs have gone (kept well short of
  black so they never read as pits), moss works in on floor tiles touching a
  wall, bones lie about, and carved relief panels (a coiled serpent, a rayed
  sun, a glyph face) are set into wall faces away from torches, skulls and
  monuments. The skeleton hall gets two toppled pillars and two broken
  stumps, each kept only if every reachable tile stays reachable. The sanctum
  gets two grand arches, the desert ruin arch recut whole in the temple's
  stone and mossed, standing against the north and south walls either side
  of the east door, fading like the desert one.
- tools/temple_dressing.py applies it to the shipped maps. The sanctum's
  breach only turns plain floor into the Astral Sea, so columns 31-34 stay
  bare (`KEEP_CLEAR_COLS`) and a test pins it. Worth knowing for any later
  floor dressing: runtime terrain changes (the breach, Phlegethos's
  corruption waves, the trio's churn) only act on plain floor characters, and
  a prop drawn on a tile does not go away when its terrain changes.
- Chult's jungle floor is dressed on all five maps. Ferns (walked through)
  and dead-leaf litter (flat) are scattered over open ground; fallen logs
  three tiles long and ruin fragments from the temple's builders -- a carved
  block, a toppled head, a column drum -- are solid, and each is kept only if
  it leaves every reachable tile reachable. The jungle, the cog clearing and
  the respite each get one great tree: the Feywild's giants redrawn in Chult's
  palette with dark kapok bark and long lianas, fading the same way. The run
  gets only ferns and litter, and never in the three gaps its route squeezes
  through; the temple approach gets no tree (the pyramid is the landmark) but
  four carved stelae flank the skull-stake avenue, which is otherwise left
  bare.
- tools/chult_floor_dressing.py applies it to the shipped maps and holds the
  rules (`check_great_tree`, `reachable`, `KEEP_CLEAR`); the suite checks the
  shipped maps against the same rules. tools/generate_feywild_great_tree.py
  takes a palette now and writes chult_great_tree_N.png as well; the Feywild
  trees are byte-identical.
- Waterdeep's plaza gate has towers. A square tower of the district wall's own
  brick, with the gate's grey stone at its corners, arrow slits and a
  crenellated top, stands a tile proud of the wall either side of the two
  guards, and four of the watch's blue-and-silver banners hang along the wall
  above the two shops. The towers stand forward rather than rising because
  the wall already runs to the top of the map. Placed by the plaza generator
  (`GATE_TOWER_COLS`, `WALL_BANNER_COLS`), so both eras get them. The banner
  is the castle banner's animation in a new palette; `banner()` in
  tools/generate_castle_banner.py takes an optional palette and the castle's
  frames are byte-identical.
- The tavern gets a keg rack behind the bar, a notice board by the pantry
  door and a worn green rug under the middle table (flat, walked over). The
  pantry gets two sack piles and two produce baskets -- onions and apples, and
  deliberately no cheese, so the one cheese stays the hook. All mute.
- The ship below decks is furnished. The captain's cabin is a study now: two
  bookcases against the north wall between the portholes and a writing desk
  in front of them with a chart, inkpot and candle on it, and the hammock is
  gone -- the captain has a bed. The galley has a black iron stew pot beside
  the hearth and a butcher block with a cleaver in it; the hold has lashed
  cargo stacks against both walls and rope coils lying about; the crew
  quarters get rope; and the exterior deck has crates, barrels, a cargo stack
  and rope gathered at the foot of each mast. No cannons (it is a medieval
  ship) and no new chests: the captain's is still the only one aboard, and a
  test says so.
- New dressing is mute. `MUTE_PROPS` in src/entities/prop.py lists set
  dressing added after the examine pass; those props have no E line and are
  skipped by the interact probe, so none of the tuned examine behaviour
  changes. `FLOOR_PROPS` generalises the captain's rug: props that lie flat
  and draw under everyone (the rope coils, walkable).
- Waterdeep's people have a second word. In both the opening and the finale,
  every townsperson, tavern regular, shopkeeper and the fisherman says their
  usual line the first time Chuck talks to them and a different one every time
  after. The repeat lines live beside the originals in data/dialogue as
  `<line>_repeat`; any line without one just repeats, so the feature is driven
  entirely by the writing. It is remembered per person (townsfolk who share a
  line each still get a first word in) and for the whole session rather than a
  single visit, and a new game forgets it.
- The guards are the exception, by design: one line, every time. The fountain
  plaza's two gate guards now say exactly what the docks' north-east guard
  says, and their separate `plaza_guard` line is gone. Bobert is untouched.

- E looks at things now. Every prop in the game answers the interact key with
  a short line in data/dialogue/examine.json, where before only eighteen of a
  hundred and seventeen kinds had anything to say. The lines are written to be
  useful when it matters: the things worth scratching say so ("A tuft of
  grass. Maybe there's a cigarette somewhere in there?", "A strange flower. It
  looks like it could use a good scratch."), the things that look scratchable
  and are not say that instead (barrels, crates, rubble, furniture: too big or
  too sturdy to break with a scratch), and decoration just says what it is ("A
  very large flower.").
- The breakables and the Feywild's switch flowers are now things E can reach:
  grass, temple urns, pantry jars and jar shelves each describe themselves and
  hint at the scratch, and go quiet once broken -- except the shelf, which
  stays and says so. Props the world always turns into breakables (temple
  urns, grain-sack jars, jar shelves) share the breakable's line, so a sack
  cannot claim to be unbreakable in one place and break in another.
- Chests only open to a scratch. E used to open them too, which made the
  chest the one object where the two buttons did the same job and taught
  nothing about which one breaks things. E now reads the chest's description
  -- closed, with a hint, or open and empty -- for both the captain's chest and
  the desert ruin chest.
- Ten older prop tests pinned doors, furniture, crates and curtains as "mute"; they now
  assert each says its examine line. The captain's chest test was rewritten to
  press E, see the line with the chest still shut, then scratch it open.

- Opened the whole seam between the Waterdeep docks and the fountain plaza, in
  both the opening and the finale. Every open tile down the docks' east edge
  -- the street north of the tavern block as well as the one south of it -- is
  now a way into the plaza, and the plaza has no west wall at all: its whole
  west side, below the north wall, is the way back. The two maps read as one
  street with a map edge across it rather than a doorway between rooms.
- Crossing keeps Chuck on his row. An exit can now say it is a whole edge
  rather than a gap; he arrives in the arrival marker's column but level with
  where he left, or on the nearest open row where that row is a building on
  the far side. Without it, stepping off the top of a thirty-tile edge would
  have dropped him back in the middle of the next map every time. A test walks
  across at several rows in both eras and both directions.
- The plaza's north wall is four tiles now -- battlements and three courses of
  brick -- with the closed gate set into its bottom course and the paving
  starting right under it. At two tiles the gate, which is over three tiles
  tall, stood on the square in front of the wall like a freestanding door
  frame. The barrels and crates that sat on the old rows 2 and 3 moved down to
  the foot of the wall.

- Redrew the Feywild's root walls so they read as roots, on all five maps that
  have them: Rootways, the Tea Table, the Redcap Warrens, the Displacer Meadow
  and the Twilight Crossroads. The old tile was four parallel diagonal bands;
  tiled into a wall it became one even stripe and read as bark shingles or a
  brown rug.
- The new tile is a tangle of curved, shaded strands that only ever leave a
  tile at fixed points on its edges, at a fixed thickness, heading straight
  out -- and every one of its eight variants uses every one of those points.
  So whichever two variants land side by side, each root that runs off one
  tile runs on into the next, and the tangle is continuous across the whole
  wall. A test checks that for every pair of variants in both directions.
- Where a root wall stops above open ground its bottom row is now a front face:
  the roots curl over and hang in tapering tips into a shadowed hollow, so the
  wall stands on the floor instead of being a brown shape cut out of it. And
  along runs of wall, spaced out, a knot -- a swollen boss where several roots
  have grown round each other, one variant with a cluster of glowing caps --
  so a long wall has places in it. 174 face tiles and 23 knots across the five
  maps, all solid-for-solid, so no route changed.
- Four failures on the way to that tile, all visible in renders. Stamping a
  shaded disc along each curve let every disc paint its rim over the middle of
  the last, and the roots came out as sludge; each pixel is now shaded from its
  nearest point on the curve. Kept tight and regular, the tangle read as
  basketwork. Bending the curve's control points also bent it where it crosses
  the tile edge, so the same edge point was a different width in every variant
  and the seams showed; the bend now lives only in the middle of each root.
  And with every gap drawn near-black, the edges -- where roots may only cross
  at their own points -- became a line of dark dashes along every tile
  boundary; ordinary gaps are a softer shadow now, with the deep holes kept
  inside the tile. A fifth, caught by the seam test rather than by eye:
  deciding which end of a root owned an edge pixel by the nearest point on
  the curve failed where a root looped back past its own start.
- Dressed from each map's generator and written straight into the shipped maps,
  like the mushrooms and great trees, and each generator's own route check
  treats the new pieces as the wall they are.

- Extended the great trees' see-through fade to everything else big enough to
  hide somebody. Two routes to the same behaviour.
- Big props thin while a walker stands behind them: the ship's two mast sails
  and its bowsprit, the sailing cog in the Chult jungle and the one docked in
  Waterdeep, the cloud tower arch, the desert ruin's gate arch, the castle
  turrets and the Tahuya cabin, alongside the great trees. Each kind now says
  how much of its bottom edge stays solid -- a mast's foot, a tree's roots,
  the cabin's porch, which Chuck walks on and which would otherwise fade under
  his own feet.
- Overhead tiles thin a whole connected canopy at a time: the market awnings,
  the city gate, the oasis palm crowns, the jungle's exit canopy, the sewer
  outflow and the Feywild's hedge openings and crawl-throughs. The map labels
  each connected piece of overhead art once, and anybody standing under any
  tile of it -- measured a little above the feet, because a rat whose head is
  under the canvas is under the canvas -- thins all of it. Fading only the
  tiles a character touches would cut a rat-shaped hole in the cloth. Other
  awnings on the same street are left alone.
- Anybody counts, as with the trees: an enemy under an awning is a hit the
  player would otherwise not see coming. Faded tiles are baked per step and
  cached, for the same reason the tree's are.

- Gave the title screen music: a very quiet space ambience. An original
  128-second loop at 60 BPM in D Lydian that does almost nothing on purpose --
  slow pad chords that take seconds to bloom and overlap so there is never a
  gap, a low drone so the room has a floor, sixteen single high bells placed
  the way stars are (irregularly, never two at once) and four reverse swells
  breathing in underneath. No percussion and no melody. The raised fourth is
  the one strange colour, the tower theme's trick for height used here for
  distance; the middle eight bars move the chords higher and thinner, then
  come home into the loop.
- Subtle twice over: mastered with a low ceiling (peak 0.48), and given a
  stream trim of 0.5 so it plays at half the volume of every area theme.
- The title used to stop the music on entry. It starts this track instead, and
  the dev checkpoint menu going back to the title leaves it playing rather than
  restarting it, because re-requesting the same stream is already a no-op.
- The tests state "subtle" as properties of the score: slow, no percussion,
  chords changing no more often than every eight seconds, fewer than one
  non-chord sound every four seconds, no two bells within four beats of each
  other and not at regular intervals, and a quiet trim. The first draft of the
  density check counted a chord's four voices as four notes and failed a score
  that was plainly sparse.

- Planted great trees in the Feywild: eleven tiles across and fourteen tall,
  a trunk three tiles wide on a solid three-by-two footprint, roots running
  out across the ground and one broad crown. No face. One per map on the nine
  maps with room for one -- Rootways, the Tea Table, the Needle Garden, the
  Redcap Warrens, the Displacer Meadow, the Mushroom Underways, the Luminous
  Rapids, the Twilight Crossroads and the Cloud Staircase -- because a tree
  this size is a landmark, and two on one map start being a wood.
- Drawn with the title screen's shaded primitives in the Feywild's own
  palette: violet-brown bark with twisting ridges and a seam, teal-green
  leaves, moss on the shaded side of the base, the region's motes caught in
  the crown. Three variants.
- Two first-render failures. The crown was thirty separate balls and came out
  as a tiered cake with the trunk showing through a gap in the middle; it is
  one shaded dome now with leaf masses as bumps on it, rimmed only where they
  break the silhouette. And two knots stacked up the trunk read immediately as
  a pair of eyes -- the one thing asked for was no face -- so the bark splits
  along a seam instead.
- The spots were chosen by measuring, against four rules the suite now checks
  on the shipped maps: the footprint is plain ground, there is open ground all
  the way round it, nothing that matters (enemy, arrival, Ashtray, breakable,
  exit) stands under the crown, and the trunk cuts nothing off.
- A crown fourteen tiles tall can hide somebody completely, so the great trees
  thin out while anybody -- Chuck or an enemy -- is standing behind one, and
  come back when they leave. Roots and the base of the trunk stay solid with a
  short ramp into the thinned part, so the tree keeps standing on the ground.
  The thinned sprites are baked once per step: fading with surface alpha at
  draw time drew a black box across the base on the first try.
- Planted from each map's generator and also written straight into the shipped
  maps, the same way the mushrooms are. The earliest Feywild maps carry
  vegetation their generators do not reproduce, so regenerating Rootways to
  plant a tree would have cut down every other tree on it.

- Turned the title-screen Chuck round to face the viewer. The first version
  drew him side-on, turned away towards his cigarette, so what showed was the
  back of the jacket and legs coming out from under it at angles that only
  work on something facing the other way. Front-on, the jacket hangs open over
  his pale chest with both lapels standing up either side of his head, each
  panel with its own pocket flap and folds, the one on the stone side turned
  away from the light. Only the head turns -- three-quarters, towards the hand
  with the cigarette.
- Two things that went wrong on the way. Both legs first came down the same
  line and merged into one thick one; the knees are apart now and the shins
  cross, feet pointing opposite ways, which is what reads as crossed ankles.
  And the head sat where it was designed and a rat grew a neck. It is drawn
  on its own sheet and set down into the collar, and the hand, the cigarette
  and the exhale point all follow it down by the same amount.

- Rebuilt the title screen: Chuck, large, leaning on his own name in cracked
  stone against the Astral sky, having a smoke. No subtitle.
- It is the one scene drawn at twice the game's resolution. Everything else is
  320x180 scaled up four times, which is right for a one-foot rat in a large
  world and wrong for the one moment he is meant to be looked at. A scene can
  now ask for a bigger canvas (`canvas_size`); the title asks for 640x360 and
  the game scales that up twice instead of four times. At that size Chuck is a
  hundred and forty-five pixels tall, and the half-lidded stare, pink ears,
  long snout with whiskers and two incisors, fur grain, the jacket two sizes
  too big and the cigarette are all things a player can actually see.
- Made the same way as every other asset: drawn by code, no anti-aliasing, a
  fixed ramp per material, dithered between tones. What is new is a set of
  shaded primitives -- capsules for limbs and tail, ellipsoids for skull and
  snout -- lit from the upper left like the rest of the game, unioned per part
  so a snout built of three blobs reads as one snout, each part with its own
  dark rim so an arm in front of a jacket reads as one.
- He moves. Tail sway, blinks, and every few seconds -- rests of different
  lengths, so it never becomes a metronome -- he lifts the cigarette, drags
  while the ember brightens, lowers it and lets the smoke out. A thread of
  smoke comes off the ember the whole time, leaning away from his face. He is
  split into layers so none of that needs every combination baked: tail
  behind, body with eyes open or closed, near arm in five positions. The
  generator writes where the ember and the mouth are in each frame, and a test
  checks the ember in the metadata is the ember in the art.
- Four things the first renders got wrong. The far arm reached out instead of
  resting on the C; it now goes up over the top of the letter and hangs down
  its face, and a test checks his hand overlaps the stone. The eye came out as
  sunglasses, because the lid was drawn as a black band -- it is fur now with a
  dark edge. A pale neck blob read as a scarf and a belly-white cheek read as
  a moustache. And the nebula, thresholded out of a busy grain field, came
  back spotted like a leopard; it is one smooth density through a dithered
  ramp now, the way every lit surface in the game is shaded.
- The smoke was invisible on the first pass: one-pixel grey specks are the
  exact colour and size of the nebula's star dust. Each puff has a core and a
  thinner halo now, spawned close enough together to read as a ribbon.

- Added a death count. Top right, just left of the cigarette count and in
  the same quiet voice: a rat's skull over crossed bones and the total. The
  skull is a rat's rather than anybody's because of the long snout tapering
  to two incisors, and the two round ears, which a real skull would not have
  and a rat at thirteen pixels cannot do without. Pale bone with a dark
  outline, so it reads on sand, on night streets and on Feywild green alike.
- Two kinds of death go into it. The ordinary one -- Sanity running out, or
  a drop into the Astral, which hands off to the same respawn -- is counted
  once per vanish; a hit that lands while Chuck is already gone is the same
  death. And the three cutscenes where the same thing happens to him on
  screen: the fall to Chult, the fall into Hell and the landing in the modern
  city, each of which plays the established impact, vanish and return. Each
  counts at its vanish. The other eight cutscenes, where he lands on
  something and gets up, count nothing.
- That split is tested by running every cutscene in the game from its first
  frame to its handoff and checking which ones moved the number, rather than
  by asserting a list of names -- so a future cutscene that kills him, or one
  of these three losing its death, fails the test instead of passing it.
- The count only goes up. The cigarette count rewinds on the same respawn,
  because what Chuck picked up past the checkpoint is lost with him; a death
  is not something that can be lost that way, and the test asserts both
  happening on one frame with only one of them undone. It carries through
  every handoff, saves at the Ashtray alongside the cigarettes, restores on
  CONTINUE and resets on NEW GAME. Saves written before it existed load with
  none recorded, and forged values are rejected like every other field.
- One consequence of saving it the same way as everything else: deaths since
  the last Ashtray are not on disk until the next one, so quitting and
  continuing forgets them along with the rest of the run since that save.

- Built the undead ruins up to the size the rest of the region kept implying.
  Every column on the map was a broken one, because the whole ruin vocabulary
  is fragments -- which is right for the hub, where the scattered rectangles
  are pieces of this building, and wrong here, where this *is* the building.
  Nothing on it was ever the size those fragments were fragments of.
- A great order: pillars twenty-eight pixels across and up to seven tiles
  tall, against the old ones' twenty by three. Ten of them, flanking the way
  in, the courtyard door and the deepest room. The footprint stays a single
  tile so a pillar can stand anywhere a small column could and can never be
  the reason a room closed; the stone overhangs its tile by six pixels a side,
  the way the eastern castle's banners overhang theirs. Shaded across the
  whole width rather than in three strips, because a cylinder is a gradient
  and the strip version is a flat board with stripes on it.
- A gate arch over the door the player arrives at, five tiles across and six
  and a half tall, and the one piece of the building still whole. A ruin where
  everything has fallen is a field of rubble; one thing left standing is what
  says how high the rest of it was. It is a single sprite rather than five
  tiles of art, because what makes an arch read is the curve running unbroken
  from one pier into the other and a curve cut into sixteen-pixel tiles is a
  staircase.
- The arch's first version was the ring alone under a cornice, and a ring with
  daylight either side of it is a croquet hoop. An arch is a hole in a wall,
  so the spandrels are filled: what stands there now is a piece of gatehouse
  with an opening cut through it, and the voussoirs are the joints round that
  opening rather than the whole object.
- Only its two piers are solid, and they are the wall either side of a door
  widened to three tiles. The sprite is anchored on the tile Chuck walks
  through, so it sorts against him correctly -- behind him on the way up to
  it, in front of him once he is through -- and the opening is transparent, so
  he shows through it while he is under the crown.
- The outer wall is two leaves thick. One tile of stone is a garden wall, and
  a building with rooms, a courtyard and a gate in it was built thick. The
  inner leaf is broken much harder than the outer one, which is how these
  walls actually fail -- the facing stays up and the rubble core goes -- so
  the thickness comes and goes along the run, which is what stops two tiles of
  wall reading as one tile of wall drawn twice. Every doorway is cut through
  both leaves; a door that goes through the facing and stops at the core is a
  niche.
- The pillars are placed before the fragment dressing rather than after. The
  ruin dresser never writes on a tile that already has something on it, so
  going second meant a great pillar and a broken one could want the same tile
  and the great one lost.

- Took the wooden frame off the Feywild's tea table. There was a lip drawn
  round the whole ring of the shadow, and from above at this distance a thin
  border round a dark rectangle is a picture frame rather than the edge of a
  table. It is gone, and with it the three tiles, the three sheet rows and the
  three draw functions that made it -- including the west and east rails added
  last session to stop the horizontal art reading as a ladder, which was the
  right fix for the wrong object.
- Nothing about the scale gate depended on it. The shadow was already the tile
  too low for anything bigger than Chuck, so the cache and the southern exit
  are gated exactly where they always were; the test now says that out loud
  rather than testing the frame.
- The shadow does the whole job on its own, so it was redrawn to be able to.
  It is the Feywild's own ground tile at the same speckle positions with every
  colour taken to a bit under half -- shade being the same floor with less
  light on it, which is what makes a shaded floor read as being under
  something where a differently-coloured floor reads as a different room.
- Two things went with the old shadow. It carried a green line along its
  bottom edge, which on a field ten tiles deep drew ten stripes across the
  underside of the table and read as floorboards. And its pollen glow: every
  ground tile out there catches one lit mote, and the one place in the Feywild
  where nothing should be catching the light is under the furniture.
- The two legs moved up against the table. A leg is seventy pixels of sprite
  drawn upward from the bottom of its tile, and row 32 is the row that puts
  its top a few pixels into the tabletop, so the leg meets what it is
  carrying. Standing where they were, on the old frame, they were posts with
  five tiles of gap above them -- legs holding nothing.

- Put turrets on the knight courtyards and widened the walls under the
  banners. The corners had a drum tile each, which at one tile apiece read as
  a slightly different piece of wall -- and a corner tower exists precisely
  because a corner is where a castle wants height. The corner is an object
  now: three tiles of stone with a slate cone on it and a red-and-gold pennant
  on the finial, standing tall enough that the curtain runs into its base. It
  is the only thing in the fragment that rises, which is what makes the walls
  beside it read as walls of something. Four on East 5, one per corner, and
  two on East 7.
- The pennant is the same red and gold as the banners hanging below it. The
  castle already says whose it is at eye level; saying it again on the
  roofline is what a real one does, and it ties the two objects together as
  one house rather than two ideas.
- The banners were hanging on the open ground in front of a one-tile curtain.
  A banner is two tiles of sprite drawn upward from the bottom of the tile it
  stands on, so two thirds of the cloth came down past the bottom of the wall
  and lay on the courtyard flagstones -- a banner as tall as the building it
  was on. The wall grows a buttress under every one of them now, three tiles
  wide and one deep on the face that shows, and the banner hangs on that: the
  cloth covers the buttress and the curtain behind it and stops at the wall's
  own base. Two banner tiles collapsed into one in the process, because the
  ground it hangs over no longer varies -- it is always stone.
- That makes the castle pass the first one in the desert that adds stone
  rather than swapping it, and a gate out here is a hole in a wall that looks
  exactly like the floor either side of it -- there is no reading of the
  characters that tells a buttress it is about to plug one. So every block is
  written, the map is flooded, and the block is taken back off if anything
  stopped reaching anything. The test builds a wall whose only gate has a
  buttress-sized hole under it and asserts the pass comes away empty, then the
  same wall with room beside the gate and asserts it does not.
- Flooding from whichever open tile came first was the first version of that
  guard and it was wrong in the quiet way: East 7 is nine worlds in pieces and
  its first open tile is inside one of three sealed rooms, so every block
  measured itself against a flood that never reached it and was refused. East
  7 came back with no turrets and no banners at all. The guard floods the
  largest connected piece of open ground instead -- the playable map.
- East 5's south-west corner stands on the lip of a chasm and cannot have all
  nine tiles of a turret block. Refusing those outright left one corner of a
  four-cornered courtyard bare, so a block is clipped to what it can stand on
  and the sprite overhangs the drop, which is what a tower built on a cliff
  edge does anyway.
- Two more stale exact-inventory assertions in the East 5 suite, both of which
  now include the new stonework: the perimeter vocabulary, and the list of
  which character belongs to which world. Worth noting that the banners used
  to be able to land in a gate -- they hung on open ground, and a gate gap is
  open ground, which is why the old test had to count them as gates. They are
  stone now and cannot.

- Fixed the Feywild's giant tea table. It had four legs under it, in two
  pairs four rows apart in the same two columns. A leg is seventy pixels of
  sprite drawn upward from the bottom of its tile, so a pair four rows apart
  stacks into a hundred and thirty-four pixels of continuous post with a joint
  halfway up it -- which is a pillar, not a table with legs. Only the front
  pair is left, feet on the south lip and rising away under the table, which
  is the pair this angle has any reason to show.
- Nothing stands loose in the western aisle any more either. Three chair legs
  were scattered there, each on its own in open ground with no seat over it
  and no second leg near enough to belong to the same chair, so what they read
  as was fence posts nobody built a fence out of. The freestanding legs east
  of the table had already been cut for exactly that reason; these are the
  same object, and the prop, its tile and its sprites are gone with them.
- The table's lip is three tiles now rather than one. A beam has a direction,
  and the north-south art -- a band across the top of the tile -- repeated
  down the west and east edges drew eight loose planks with a gap between each
  one, which reads as a ladder bolted to the furniture. The side runs have
  their own tiles, drawn along the tile instead of across it and mirrored so
  the lit face is the outer one, and the four runs together now outline the
  table's actual footprint as a closed rectangle.
- Both new tiles are the same overhead lip the old one was: Chuck walks under
  every tile of it and nothing larger does, which is the whole scale gate on
  this map. They are in `LARGE_ACTOR_PASSAGE_TERRAIN`, and a test walks the
  ring and asserts it is unbroken, so the cache and the southern exit stay
  reachable by Chuck and unreachable by anything else.
- Regenerating the map turned up a landmine worth recording. The Feywild's
  trees were added to the six earliest maps by editing the shipped text files
  directly and were never written into those maps' generators, so running the
  tea table's generator dropped a hundred and eighty trees and the dense
  blocks went back to reading as flat green slabs. The pass is now in the
  generator, where it can be run twice and come out the same both times: 84
  grove trees, 83 shrubs and 5 oaks, against the 89/89/5 that shipped. The
  other five maps in that group still have the same gap and will lose their
  wood the day anybody regenerates one.
- Planting as the sweep went was the first version of that pass and it eats
  its own map -- a tile dressed on one row is no longer dense growth for the
  neighbour test on the next, so the mass shrinks ahead of the sweep and the
  last kind placed came out at 8 instead of 83. Every tile that can take a
  tree is found before any of them is planted.
- One more exact-inventory test rewritten as a rule. Phase 9 pinned the
  Feywild's overhead characters as a literal dict, which fails the day a new
  overhead is added whether or not the new one is right. It now asserts the
  four cardinal boundary cuts and the table's four lips are present, and that
  every overhead -- whatever the list grows to -- is non-solid, is not also a
  floor, and resolves to ground somebody can stand on.


- Finished the collided desert's castle. The medieval fragment out east
  shipped as flat coursed ashlar: correct stone, and unmistakably a boundary
  rather than a building. It now reads as sections of a castle -- crenellation
  along the curtains, drum towers with arrow loops on the corners and on the
  stumps the broken runs end in, and red-and-gold banners hanging down the
  faces that show. 120 merlons, 16 towers and 12 banners on East 5, 32/12/5 on
  East 7, and 38/1/2 on East 8.
- It matters more here than it would anywhere else that the walls say
  something: this is the one world in the collision Chuck has never visited,
  so there is no map of it to remember and the walls are the whole of what
  anybody ever learns about the place. A wall becomes a castle wall the moment
  it is notched and has a tower on it, and it belongs to somebody the moment
  there is cloth on it.
- The banners are authored on the ground tile in front of the wall, not on the
  wall. Props anchor to the bottom of their tile and draw upward, so a banner
  on the stone would rise off the battlements like a flag on a pole; from one
  tile out, cut to exactly two tiles tall, the same upward draw puts the iron
  bracket on top of the stone and the hem on the floor. Two characters for one
  object because the ground differs -- flagstones inside the courtyard, sand
  outside it -- which is the same reason the docks has two barrels.
- Four frames of a slow lift rather than a flap. Nothing else on these maps
  moves in a wind: the fires are out and the snow falls straight down, so
  cloth that snapped would be the one thing on screen with weather of its own.
  The sway is a per-row horizontal offset growing toward the hem, because
  offsetting the whole shape made it a sign swinging on a hinge.
- The pass is collision-neutral by construction, which is the only reason it
  could be run over maps whose geometry other suites measure to the tile --
  East 8's islands, East 7's nine worlds, and the arena the horde has to
  cross. Merlons and towers are converted *from* wall, so they are solid tiles
  standing exactly where solid tiles already stood, and banners are non-solid
  and go on ground that was already open. The test rebuilds each shipped map
  with the castle taken back off it and asserts the walkable set is identical.
- East 6 gets nothing. It has flagstones from the same world and not one tile
  of wall, and conjuring a section onto it would be solid stone appearing on a
  map measured elsewhere.
- The first classification called anything two tiles thick a tower, and the
  two island maps -- where every clump of that stone is thick -- came back as
  forty towers in a heap. A mass is now crenellated into a ring and only
  corners, turns and lone stumps get a tower; the test states that as a rule,
  that towers are the punctuation and never outnumber the merlons.
- The failure worth recording is the character choice. Three of the four
  characters first picked for the new tiles were already in MARKER_DEFS -- two
  arrival anchors and a desert transition -- so they counted as castle on maps
  that had never been regenerated, and a blanket rename compounded it by
  renaming the live markers as well. Recovered by reverting `tilemap.py` and
  re-adding only tiles on characters verified absent from *both* tables.
  TILE_DEFS and MARKER_DEFS are global across every map in the game; a
  candidate character has to be checked against both, every time.

- Furnished the modern city. Every block was a road, a kerb, a pavement and a
  wall of building, and between those four things nothing stood on the ground
  at all -- which is why a street here read as a diagram of a street. It now
  has lamp posts along the kerbs, three hydrants a map, and a stop sign where
  a road actually ends: 134 lamps, 35 hydrants and 11 signs across the twelve
  city maps.
- The night city's lamps are lit and the day city's are not, which is the
  whole of the ask and is two separate things. The sprite has a lit twin --
  two files rather than a two-frame sheet, because this is a state and not an
  animation -- swapped at spawn the same way the cabin's table picks its woken
  one. And the *light* is a field of additive pools on the pavement that only
  the night maps build.
- Night is read off which tileset a map draws with rather than off its name.
  The two cities are the same streets at different hours, and the sheet is the
  one place that difference was already recorded.
- The pools only ever add. There is no darkening pass, because the night city
  already draws with its own night sheet -- multiplying that down to light it
  back up is re-lighting a room that is already lit, and what came out of
  trying it was a street darker everywhere except directly under the lamps,
  which reads as fog rather than as night. Each pool carries its brightness in
  its colour rather than its alpha, because an additive blit ignores alpha:
  drawn the obvious way, white on low alpha, every lamp added 255 to
  everything under it and the street came back as a row of white discs.
- One placement rule makes all three safe by construction rather than by
  inspection: nothing stands anywhere but the pavement tile against the kerb,
  which is where real pavements are furnished and is what guarantees a lane
  behind it. The pass then floods each map before and after and refuses to
  return one whose reachable set differs by anything other than the tiles it
  just filled.
- Three failures worth keeping. The first version placed lamps before the
  sparse things, so every tile a hydrant could have wanted was already a lamp
  post: 180 lamps and not one hydrant or sign. The second spaced lamps by flat
  distance, so a lamp on the north pavement suppressed the whole of the south
  pavement nine rows below it and every street came back lit down one side --
  spacing now runs along each kerb, and each side of a road is its own kerb.
  The third wanted three tiles of pavement behind every post, which left City
  Day 5 -- a canyon two tiles wide each side -- with no lamps at all.
- Two Phase 11 tests pinned the exact prop inventory of their map, which was
  true when a city block held nothing but its own scene and stopped being
  true the moment the streets were furnished. They now assert the scene's
  props at their counts, that there is some furniture, and that there is
  nothing else -- so they still catch a stray prop without failing every time
  a road moves a lamp.

- Furnished the fountain plaza. It came out of its first pass correct and
  empty: two shops, a gate, a fountain and a stall, all of them pressed to an
  edge, and forty-two tiles by seven of unbroken paving between them. That is
  more than two screens wide and most of one tall; the docks, which this
  square is meant to feel like, never manages worse than forty-nine tiles and
  its worst case is a single row deep. The largest bare stretch here is now
  twelve by five.
- Everything in the pass is existing Waterdeep vocabulary -- the barrels and
  crates that stand outside every building in the port, the weeds that come
  up between paving stones, and one more stall in the market's own awning
  grammar. No wall moved and no route changed. The rule the clusters are laid
  to is: nothing wider than three tiles, and four tiles of open paving
  between one stack and the next.
- The weeds are the useful half of it. They are non-solid, so they can never
  narrow a route, and each one has a cigarette under it -- which was the
  other thing the square was missing. Every other map in the city has
  something in it worth scratching at; this one had nothing, and now has
  fourteen tufts and three lying loose.
- Two tests state the pass rather than the taste: the largest all-paving
  rectangle is under half a screen and within a factor of three of the
  docks', and every dressed tile is checked against what was actually
  written, so a cluster can never silently land on a shop front or a stall
  post. The navigability flood now proves all four corners as well, because
  a furnishing pass is exactly the kind of change that walls one off.
- Fixed where the return puts Chuck. The finale checkpoint carried an
  explicit position of (32, 208) -- tile (2, 13), which is open harbour, and
  water is solid on this map, so coming home from the desert dropped him
  inside a solid tile seven tiles off the end of the pier. It now carries no
  position at all and lands on the map's own player marker: the plank beside
  Bobert's barrel that the game opened on. Sharing the opening's marker means
  the two spawns cannot drift apart again, and it says the thing the phase is
  about better than any placement of my own would -- he is standing exactly
  where he started, with Bobert still asleep beside him and the water gone
  teal.

- Added a shared 48x34 fountain plaza through the docks' open eastern street.
  Its Waterdeep-scale square includes an animated stone fountain, guarded
  closed northern gate, blacksmith forge and anvil, alchemist bottle display,
  and a small produce stand. The route works in both directions in both eras.
- Both states use the same plaza map and collision. Opening Waterdeep keeps its
  original palette and five essential plaza inhabitants; the finale selects
  the midday sheet and adds six more townsfolk. Shopkeepers only answer Chuck
  with short lines—there is no buying, currency, equipment, or inventory UI.
- The existing Waterdeep Ashtray preserves the return flag across save and
  Continue, including the plaza's midday art and larger crowd. Phase 14's
  acceptance criteria are complete; no Phase 15 contract exists yet.
- One test from the harbor slice had to be rewritten rather than re-pinned.
  It asserted that the return flag gated exactly one checkpoint, which was
  true when the docks were the only map with a midday version and stopped
  being true the moment the plaza got one. It now states the rule instead of
  the list -- everything the flag gates is a finale entry, the docks' own is
  among them, and none of the opening entries is -- so the next shared map to
  gain a second state breaks the thing this protects rather than the test.

- The returned Waterdeep harbor now gains one large docked cog, a fisherman
  with a small animated rod/line/bobber idle, two extra dock workers, and three
  market browsers. All six people use the established human scale and remain
  non-colliding on safe authored ground; the ship sits over water and only
  meets the existing south pier.
- This population and scenery are driven solely by the durable
  `waterdeep_returned` flag. A new game still sees the original quiet docks,
  unchanged geometry, and unchanged routes. Focused tests lock the state split,
  placement safety, count increase, ship-art reuse, and fishing idle.
- The shared eastern fountain plaza is now the next Phase 14 slice.

- Phase 13's return cutscene now hands directly into playable Waterdeep rather
  than ending at the title. It records `waterdeep_returned` first, carries
  Sanity and the existing progression set through the shared checkpoint
  loader, and fades from the cutscene's white into the docks without treating
  the crossing itself as a save point.
- Starting and ending Waterdeep use the same `waterdeep_docks.txt` geometry.
  The durable return flag selects a separate midday rendering sheet: brighter
  stone, timber, canvas, and masonry; sky-reflecting rather than glowing tavern
  windows; and noticeably teal animated harbor water. The northern wall torch
  fixtures remain in place but their flame frames are extinguished.
- Added `Waterdeep Finale` as the explicit return checkpoint and focused Phase
  14 coverage for the handoff, shared geometry, state-selected sheets, palette
  shift, and unlit fixtures.

- Five things in the cabin now answer when you look at them: the table map, the
  fridge, the lava lamp, the woodstove and the wall hanging. The table keeps
  its line in both states, because the planar question belongs to the walk
  trigger rather than to the prop, so describing the map never competes with
  being asked whether to step into it.
- The small couch moved a column west and a small square table stands in the
  gap east of it. The sink graphic moved to the east end of its counter.
- Outside: a few firs down the narrow walk on the cabin's east side, alternating
  sides so the way through stays open; the circular object moved south-east off
  the edge of its clearing and into it; the astroturf strip is two rows shorter;
  and the southernmost mushroom light is gone.

- The two firs flanking the cabin's driveway are gone, and the corridor they
  stood in is cleared through the whole planted band rather than only its top
  few rows. The track had been stopping short of the opening, so trees were
  standing where the dirt should have carried on.
- The understory is kept off the track too. It plants itself wherever there is
  a fir within a couple of tiles, so clearing the trunks only invited salal
  into the gap they left and the mouth grew shut again.
- The Astral Sea closes the cabin grounds on every side, one block wide. The
  wood is impassable well inside it so it is never somewhere Chuck stands and
  looks at -- it is there so the ground ends in the same thing it ends in
  everywhere else in the game rather than at an invisible wall.

- Phase 12 has an ending. Standing at the awakened table asks `Enter planar
  portal?`; NO closes with nothing said, and YES plays the desert arrival.
- The question belongs to the awakened map alone. The trigger is authored in
  the map always and simply not built while the table is ordinary, so the
  unawakened table has no planar interaction rather than having one that stays
  quiet.
- The crossing opens out of the table's own surface -- the same portal shared
  with the city oval and the Douglas fir -- swelling until it is the whole
  screen and then draining to light rather than cutting to black. The desert
  fades up out of that same light, because he is going from a cabin at night
  into the middle of a day.
- It ends the way the Douglas fir crossing does: recorded as
  `desert_transition_completed` against the save that still points at the
  cabin, then back to the title. Continue returns to the cabin rather than to a
  desert that does not exist. A test holds the out-of-scope line -- no desert
  map, no desert tileset, nothing playable on the far side.

- The opening in the Douglas fir at the end of Phase 11 is a planar portal now
  rather than a black hole: grey with light suspended in it, turning slowly,
  the same surface as the oval standing in the wrecked city block. The two are
  the same crossing seen from either side, so they share the surface outright
  instead of being drawn twice and kept in step by hand -- the city portal's
  own frames come out byte-identical to before.
- The small opening pushes its colour further from grey than the city oval
  does. The lobes are the same shape in both, but across twenty pixels rather
  than sixty they cover too few to be told apart and the whole thing flattens
  into one tone.

- The wood opens north of the cabin as well as south. The stand bows away from
  a second bay above the building on the same curve the fire bay uses, thinning
  toward the middle, with the same firs and the same salal and huckleberry
  under them.
- A driveway's width of dirt runs out of the top of that opening and away
  through the trees -- which is how anyone got a cabin onto this ground at all.
  It stops two rows short of the border so the track goes out of sight behind
  the trees rather than ending against the edge of the map, and the columns
  either side of it are kept clear of trunks: a fir is three tiles of canopy
  wide and one standing against the track hides the whole of it.
- The circular object has moved from the far north-west into that opening, just
  west of the track.
- The understory now follows every fir on the map rather than only the west
  stand's. It was reading the trees off the list that stand was built from, so
  the thickened tree lines north and south stood on bare ground while the west
  side had brush under it.

- The strip of astroturf from the reference photographs is laid on the dirt at
  the foot of the cabin steps, running seven rows south and stopping short of
  the fire. It is walked on, not around. The tile has to look wrong to be
  right: flat, too even and too green against a forest floor that is none of
  those, with every fibre leaning the same way and fir needles fallen on it.
  The green is taken well down, though -- it is night out there and the whole
  map is lit for it, and at daylight saturation the strip glowed like a lit
  panel lying in a dark wood.
- Note: the photographs show the strip at the cabin's back door, and the
  exterior has only the one south doorway -- so it runs from those steps.

- A mounted Canada goose head hangs on the west wall between the map table and
  the couch above it. It lies on its side: the plaque flat against the wall on
  the left, the neck running out horizontally, the head and bill over the room
  on the right, which is what a mount on a side wall looks like from this
  camera. Stood upright, however small it was drawn, it read as a decoy on the
  floor in front of the wall. The neck is drawn thin, because a goose's is:
  thick enough to match the head, the bird came out as a sea lion. Interacting
  says `It's a mounted
  goose head... did it just wink?` -- three dots rather than an ellipsis
  character, matching every other line in the game.
- The mini fridge is black. White, it was the brightest thing in a dark olive
  room and pulled the eye off the table beside it; the handles carry the shape
  now.
- The real cabin's knotted wall hanging is on the panel to the right of the big
  couch's window: two weathered sticks with a square-knot panel between them,
  twisted cords sweeping down and inward to a point, and a cut tassel below.

- The cabin's north wall is three rows of panel rather than one. Everything
  hung on it -- one curtained window centred behind each couch, and the door
  between them that does not open -- is taller than a single tile, and on a
  one-row wall the tops were clipped by the edge of the map and the bottoms sat
  out on the carpet. The room reflows below it; the map is 21x26.
- The lava lamp runs at its own frame rate, eleven times slower than the
  stove's. Animated props shared one pace, and at the fire's rate the blobs
  shot up and down like a boiling kettle.
- During the lightshow the lamp casts its own pool: smaller, redder and
  steadier than the stove's, swelling on the same slow beat its blobs move on.
  The painted spill on the table top is gone -- with the room lit normally it
  read as a stain, and in the dark the projector scene gives it a real one.
- The cabin's two west-facing chairs and the entities in them are pushed flush
  against the east wall, so the seated pair face across the room rather than
  sitting out in it.
- A lava lamp on a small pale blue side table stands on the strip between the
  woodstove and the east wall -- the one piece of floor in the room with
  nothing on it and a wall to put a lamp against. Six frames, with the blobs on
  separate cycles so it never reads as a pulse.
- A door in the north wall between the two couches that does not open. It uses
  the same interaction the cabin's west door already has, so both say the same
  thing rather than one of them growing its own line.
- Curtains, drawn, on the wall behind each couch. They hang a row above the
  couch and are exactly two tiles tall: taller and the pelmet -- the part that
  always shows over the couch back -- is clipped by the top of the map.

- The lightshow cue lost its neon synth lead. The tune is carried by a jaw harp
  and two new Tuvan throat voices instead: a kargyraa growl holding the root,
  built from a sub-octave pulse under a saw because that is literally how the
  sound is made, and a sygyt overtone whistling the hook's own contour two
  octaves below where the synth used to play it. Same notes, same order, no
  longer up in the air.
- There is roughly six times as much jaw harp: a syncopated figure of its own
  every bar, plus an answer to each melody note in the gap after it.
- The tree line below the fire bows away from it, so the wood opens out around
  the fire in a bay rather than stopping at it in a straight fence. The
  thickening band stays the same few rows deep everywhere and it is the line it
  hangs from that moves -- stretching the band to fill the bay instead just
  planted the opening.

- The wood on the cabin grounds has an understory: evergreen huckleberry and
  salal, roughly 460 shrubs through the stand. Firs on bare ground read as
  posts standing in a lawn, and a Douglas-fir wood in this part of Washington
  is never bare underneath.
- The two are drawn to be told apart. Salal is a low mound of big leathery
  ovals on reddish stems; huckleberry is an upright spray of small glossy
  leaves with bronze new growth at the tips. Three cuts of each, picked by
  tile, so a stand never repeats in a visible rhythm. No berries -- at this
  scale a red dot reads as an insect, not fruit.
- Both are scenery Chuck walks through rather than around. He is a foot tall
  and these are shrubs; solid brush this thick would have fenced off the wood.
- Placement follows the trees rather than covering the map: a tile only gets
  brush if there is a fir within two tiles of it, which keeps the clearing, the
  trail and the fire circle open without any of them being named as exclusions.

- The trail and the lit mushrooms end at the fire on the cabin grounds. They
  used to run on south past it and off the bottom of the map, which read as a
  way out that goes nowhere. The last two lights turn in toward the fire circle
  and stop there with it, so the lit path leads somewhere.
- Everything south of the fire is the forest the cabin stands in: five rows of
  stand thickening toward the dark, then trees closed over entirely. The
  thickening is drawn off the same authored seed as the western stand, because
  a modulo pattern planted exactly the tree farm that stand was built to avoid.

- The cabin interior is shorter north to south. The hardwood room ran eleven
  rows deep, which at native scale put most of a screen of empty floor between
  the north wall's table and fire and the south wall's sink and door, so the
  two halves of the cabin never appeared together. It is six rows now and the
  map is 21x24 rather than 21x29.
- Everything below the carpet is measured from the floor band rather than
  written out, so the sink, the sealed room, the doorway and the arrival cannot
  drift apart if the room is resized again -- and the interior tests derive
  their rows from the same constants instead of restating them, which is what
  had let them record positions rather than intent.
- The west counter shrank with it. Its sprite is exactly as tall as the room is
  deep, and left at its old height it stood up through the carpet and across
  the map table.

- The music lifts with the lightshow. Waking the table map switches the
  interior to an awakened arrangement of the cabin cue: the same thirty-two-bar
  root cycle, the same elastic-bass figure and the same two neon hooks,
  imported from the calm version rather than rewritten, with the Beholder
  fight's language laid over the top -- a choral ostinato grinding the flat
  second, brass answering the hook, timpani and toms under a double-time kit.
- That works because the two share a modal world: the cabin is D Dorian and the
  boss theme D Phrygian, one note apart, so the flat-second grind sits over the
  cabin's own harmony without either being retuned. It runs at 132 against the
  cabin's 112 and takes the boss theme's headroom, which is most of why it
  lands as a lift rather than as a remix.
- The lift belongs to the room the aurora is in. The authored cue for both
  cabin maps is unchanged, so door crossings before the awakening still restart
  nothing, and walking back outside afterwards drops the intensity again rather
  than carrying it into the trees.

- Waking the table map now turns the cabin lights off. The interior is lit by a
  Northern Lights projector: broad soft bands sweeping the room in slowly
  cycling colours, a held scatter of blue stars behind them, and the woodstove
  throwing a dim orange pool that stays orange while everything else changes.
- Every layer carries its brightness in its colour channels rather than its
  alpha. An additive blit adds the source channels and ignores alpha, so drawn
  the obvious way -- white on low alpha -- each band added 255 to everything
  beneath it and the room came out as saturated tartan.
- The bands are drawn once in grey and tinted on the way to the screen, and
  sweeping them is a blit at a moving offset, so the whole effect costs three
  tinted blits and a fill per frame however many bands are in it.
- The palette is walked rather than jumped between, so the room changes colour
  the way a projector does instead of flicking like a light switch.

- The cabin on the exterior map is a proper gable-roofed landmark, rebuilt to
  the reference photograph and grown from 208x150 to 370x263. Its geometry is
  written at a base size and multiplied on the way to the canvas, so the whole
  building resizes from one number without the roof, eaves and porch falling
  out of agreement.
- The cabin sorts against the back of its own porch deck rather than against
  its feet. Sorting a building on the tile it stands on is right for anything
  Chuck walks around and wrong for anything he walks onto -- the deck is drawn
  as part of the cabin, so he vanished under the decking the moment he stepped
  up. It still covers him when he is behind it.
- The doorway is three tiles wide. One tile on a building this size had to be
  lined up on before it would open.
- The deck and steps are read off the sprite the same way the mass is: a tile
  is board if the cabin fills it with the porch's own timber. The porch used to
  be a rectangle wider than the deck drawn on it, which left bare planks lying
  around the building's feet like spilled flooring.
- The firepit and the woodshed have come up from the far edge of the clearing
  to just south of the porch steps. It has a ridge
  and two roof slopes with a triangle of siding under them, a covered porch on
  its own small gable with posts and a railing, wooden steps down in front of
  the door, a lit lamp beside it, panelled windows on both visible faces, and
  concrete piers holding it off the ground.
- Its footprint is no longer a hand-written rectangle. A gable-roofed building
  is not a rectangle -- the roof reaches further at the ridge than at the eaves
  -- so the drawn mass and the collision drifted apart every time the art
  moved. The map generator now reads the coverage back off the finished
  sprite's own alpha, so collision follows the visible building by
  construction.
- The porch and stair terrain were the cabin's aged blue. Beside the warm drawn
  decking they read as a cold slab bolted to the bottom of the steps, so both
  tiles are now the same weathered wood the cabin's own porch is built from.
- The roof moss was drawn as ellipses and came out looking like toadstools
  growing on the shingles. It is short flat runs lying along the courses now,
  clumped with a two-scale offset so it is a mat with bare patches rather than
  an even speckle.

## Active Phase 12 scope

- Reworked the 80x64 nighttime cabin grounds around a compact 208x150
  procedural three-quarter-view cabin landmark. Its blue-gray wall planes,
  mossed shallow roof, raised posts, side window, south porch, stairs, and lit
  south-facing door read clearly at native scale without attempting to match
  the deliberately larger playable interior footprint. The obsolete
  north/back exterior entrance is gone; the sole south doorway is visually
  aligned with its transition and return point.
- Added the nighttime cabin grounds as Phase 12's first playable map,
  following the authored drawing's broad arrangement: irregular clearing and
  winding paths to the west, the compact cabin and south porch on the
  right, the circular `UFO` feature, firepit, firewood shed, and offset path
  lights. The mushroom-light trail now hugs the cabin's west side with a thick
  Douglas-fir stand immediately west of it. There are no enemies, hazards,
  fall tiles, or combat pressure.
- Added a dedicated Pacific Northwest tileset and procedural exterior props:
  Douglas firs, weathered blue-gray cabin siding, mossed dark roof, porch
  boards/stairs, a fire circle, shed, `UFO`, and seven color-changing mushroom
  lights. The porch boards and stairs are painted weathered blue, and the
  enlarged fire circle sits directly south of the south porch on its centerline.
  Each light derives a stable animation phase from its authored tile, so
  neighboring lights visibly cycle out of sync and cast restrained color.
- The west clearing now contains 118 deliberately irregularly spaced fir props
  rather than a visible tree-farm grid. Its western arrival is a narrow,
  slightly winding footpath, and six scratchable cigarette-grass tufts add
  small rewards along the grounds. The circular UFO is now 132x76 pixels,
  and the enlarged exterior firepit uses a six-frame flame cycle.
- The completed Douglas-fir cutscene now hands directly into development
  checkpoint `Cabin Exterior` through the shared checkpoint loader,
  preserving Sanity. The map's single physical Ashtray is the only saveable
  exterior checkpoint and is the Continue/Sanity-zero return point after use.
- The south porch and its human-scale aligned doorway recess are accessible.
  Its threshold enters the single 21x29 Cabin Interior and returns Chuck to
  the matching porch. Both directions use the established area-exit
  and shared runtime-checkpoint path; no cabin-only teleport logic exists.
- Added the authored long interior footprint with warm vertical wood paneling,
  olive-tan carpet, southern hardwood, couches flush against the north wall,
  two closely grouped east-side chairs, the long eggshell-white west-wall
  table and stools with its ordinary
  rectangular D&D map, an ordinary southern sink/counter, enlarged woodstove,
  and a full enclosed southeast room. Both interior black doorway recesses are
  now three
  tiles wide and two deep. The table's nine-tile visual and collision
  footprints now agree, contact the west wall, and leave a clear three-tile
  lane into the north living section. A matching eggshell counter/shelf now
  hugs the west wall between the table and sink, completing their horseshoe
  layout while keeping the open room clear. The counter is flush with the
  south wall, and both chair entities plus the
  fireplace sit entirely on the green carpet above the hardwood boundary.
  The table and fireplace now share one compact east/west band, with a small
  mini fridge at the table's southeast corner. Hardwood begins immediately
  beyond that band. The southeast room has been enlarged northward into a
  genuinely sealed black interior and has a west-facing solid door that gives
  the established `it's closed` interaction. The whole interior is four rows
  shorter, removing the oversized gap between the table and sink.
  The mini fridge's collision is confined to its visible base, preserving the
  southbound lane immediately east of it.
  Furniture is human-scale and provides solid, readable level geometry while
  keeping the sole south door and the interior Ashtray connected.
- Added development checkpoint `Cabin Interior` plus exactly one physical,
  saveable interior Ashtray. Continue and Sanity-zero return rebuild it through
  the same checkpoint loader used everywhere else.
- Added exactly four stationary light-formed entities in the authored seats:
  one on each couch and one in each east-side chair. The couches now sit flush
  against the north wall and both west-facing chair entities are grouped
  farther north around the living area. Their eight-frame
  gray-biased rose/violet/blue/cyan/green/yellow/amber cycle uses stable,
  distinct phase offsets and restrained local light. Both east-chair entities
  now face west; the couch occupants retain their south-facing seated pose.
- Each entity repeats its one exact authored strange line and idempotently sets
  its own durable progression flag. All four flags flow through the existing
  Ashtray/save/Continue path; no redundant `all spoken` flag was introduced.
- The bitmap dialogue font now has a tightly whitelisted procedural treatment
  for the Phase 12 Yi symbols and combining marks. It groups distorted Latin
  marks into their base character cell for typewriter timing and layout, while
  unsupported characters outside this authored set still fail loudly.
- The table map now awakens only on the first later cabin-door crossing after all
  four individual conversation flags are present. The prerequisite remains
  derived rather than stored, and the single durable awakened flag survives
  Ashtray saves, Continue, the sole doorway, and shared checkpoint loading.
- Awakening replaces only the fixed rectangular map surface on the long
  west-wall table with an eight-frame gray-biased swirling tie-dye treatment
  and restrained local light. It does not become an oval or freestanding
  portal, and it intentionally has no interaction yet.
- Rebuilt the Cabin theme as an original 103-second D-Dorian electronic loop
  at 112 BPM, then reworked its bass into a jazzier eight-hit funk figure that
  walks through thirds, fifths, sevenths, and octaves. A four-on-the-floor
  kick, backbeat, rounded pulse arpeggio, and warmer neon
  synth hook replace the Feywild-like mallet, reed, bell, and magical-swell
  palette. Sparse tuned hand-drum accents remain secondary to the cooler,
  more driving techno identity, with softened synthetic jaw-harp twangs
  answering the bass on alternating active bars. Exterior and interior request the same
  `cabin.wav`, so the cue continues uninterrupted through both ordinary doors.
- Focused exterior, interior, checkpoint, transition, and tileset suites pass,
  including full door/Ashtray reachability, reversible arrival alignment,
  checkpoint/save/Continue behavior, and the absence of enemies or hazards.
  The game renders its launch frame headlessly, and the interior's north,
  middle, and south compositions were visually inspected at native resolution.
- Focused light-entity and dialogue suites also pass, including byte-exact
  UTF-8 source strings, native glyph rendering, authored seat count/positions,
  independent animation phases, repeated interaction, and save/Continue state.
- Focused counter-awakening coverage passes for incomplete prerequisites,
  fourth-conversation non-activation, unrelated-transition non-activation,
  sole-door idempotence, runtime art selection, save/Continue, and direct
  shared-loader restoration. The awakened table was inspected at native
  resolution and the broader Cabin/checkpoint/transition/prop suites pass.
- Focused Cabin music coverage passes for duration, parseable composition,
  exact preserved bass rhythm, recurring synth hook, four-beat kick, restrained
  hand-drum palette, rendered mix/headroom, loop seam, file presence,
  and identical exterior/interior routing. All 116 repository test modules
  pass, and the game renders a clean headless launch frame.
- Overlapping interaction targets now resolve by proximity rather than by list
  order. The map table is nine tiles wide and its zone swallows the mini fridge
  parked at its east end, so walking up to the fridge answered with the map's
  line; the nearer of two targets in reach is now the one that speaks. Compared
  by centre rather than by edge, because Chuck stands inside both zones at once
  and edge distance is zero for each.
- The awakened map is now a light source rather than a lit object: it carries
  its own glow pool in the projector's current colour, and its bands are
  brightened well clear of the dimmed room. The `Enter planar portal?` question
  is authored on both sides of the table, so walking down the room to the map
  and walking up to it are the same arrival.
- The woken map is a wormhole rather than a lit rectangle: a two-armed
  spiral whose bands crowd toward a hot throat, on its own fully saturated
  colour wheel, turning two whole bands per frame so the eight-frame loop has
  no seam. It is drawn back over the projector's darkness at full brightness,
  because the portal is the reason the lights are off and so cannot be one of
  the things the dark falls on. The map's paper is repainted near-black behind
  it so the lifted rectangle has no pale table showing at its corners.
- Cabin dressing and dialogue pass: the exterior door stands ajar with the
  unlit inside showing down its east jamb, the corner side table fills its
  bay, the UFO and the outdoor firepit answer when examined (the firepit
  sharing the woodstove's line, because it is the same fire), and the two
  east-facing entities have traded lines.
- The desert arrival is now a crossing rather than a cut. It runs 21.6 seconds
  instead of 14: the far mouth of the same portal stands upright in the sand
  before anything moves, Chuck walks out of it and fades to opaque as he
  clears it, and it then folds into its own middle -- width first, then
  height, flaring as the last of it goes -- so that by the time the tableau
  holds there is nothing in frame to explain how he got there. Only then does
  he light a cigarette, using the Chult landing's exact gesture and its clean
  profile frame.
- Phase 12 gained its own eighteen-second one-shot cue, `desert_arrival`,
  written as a four-channel NES imitation: a narrow-duty pulse tune, a rounder
  pulse a third under it on the long notes only, an eighth-note broken-triad
  arpeggio, a bass walking root and fifth, and a noise channel on an offbeat
  hat with a snare on two. D Dorian rather than Phrygian dominant -- the
  augmented second is what makes a desert sound haunted, and this is an
  arrival at the start of something. It starts under the whiteout and ends on
  a held tonic under the scene's fade. Three subtle effects go with it:
  `portal_hum` (a held airy chord shimmering, fast and shallow, since written
  as a slow beat it throbbed and sounded haunted under a cheerful tune),
  `portal_collapse` (an inward *rising* rush closing on a soft knock, because
  the thing is being drawn to a point and not dropped), and `lighter`.

## Active Phase 13 scope

- Authored the Chult desert tileset. Its palette is imported from the arrival
  cutscene rather than picked again by eye, so the playable desert cannot
  silently drift away from the desert Chuck was just standing in; a test reads
  the sheet's pixels back against those constants. One sheet covers the whole
  opening five-map region -- sand, wind ripple, shadowed dune, brown canyon
  rock, ruin stone and its buried floor, dry scrub, and the oasis's water,
  grass and palm shade -- so later maps in the region do not each churn it.
- Three of its rows had to be redrawn after rendering them in place. The dune
  was drawn as an actual dune, with a lit crest and a shaded face; one tile of
  that looked right and a patch of them put every shadow at the same height,
  which read as planks laid across the sand. A tiling texture cannot carry a
  feature that large, so it carries the value instead and the dune's shape
  comes from where the patch is drawn on the map. The ruins were a pale grey
  that read as modern brick, and their floor was drawn as stone with sand
  drifted onto it, which made the inside of every ruin a tiled room dropped
  into a desert; it is now sand with stone showing through, with the joints
  running to the tile edges so they meet across boundaries and a field of them
  is one continuous pavement.
- Added `desert_central`, the 72x56 hub. Four ways out, one per side, cut to
  the same width at the same offset, with the ground in front of each kept
  clear of ruins, rock and scrub by the generator rather than by hand -- the
  phase document forbids announcing that east is the way forward, and that is
  exactly the kind of rule a later edit breaks by accident. Six broken ruins
  and six rock outcrops give the open sand landmarks to navigate by. The
  region is walled in brown rock, so it reads as a canyon floor rather than as
  a cropped rectangle of sand. Only the shape is authored so far: the maps the
  four gaps lead to are the next slices, and adding them will add markers
  rather than change the map.
- Added `desert.wav`, a loop in D at 96 BPM (75 seconds when it was
  written; two minutes now -- see the music slice below). It is the
  arrival cue's tune grown up -- same mode, same tonic, the same broken-triad
  arpeggio underneath -- so stepping out of the cutscene into the playable
  desert sounds like staying in one place. The roles are swapped, though: a
  theme played across five maps of unmarked exploration cannot lead with its
  melody, so the arpeggio and bass carry it and the reed states a phrase every
  eight bars or so and then leaves a long gap.
- The table crossing now hands off into the desert instead of ending at the
  title. That ending was correct while Phase 12 was the last thing built --
  with no playable region on the far side, recording the crossing and letting
  Continue come back to the cabin was the only honest thing the scene could
  do -- and it became a bug the moment the far side existed. It uses the same
  shared checkpoint path the Douglas fir crossing uses, carrying Sanity
  through; the desert's own Ashtray owns persistence from there, so the
  handoff writes nothing.
- The arrival fade gained a colour. Every crossing until this one went to
  black and every map faded up out of black, so the colour was hard-coded;
  this one whites out, and fading the desert back in from black put a flash
  between the cutscene and the map it hands to. `CheckpointDefinition` now
  carries `fade_from`, defaulting to black for all the existing arrivals.
- Phase 12's `test_no_playable_desert_exists_yet` has been replaced rather
  than deleted. It asserted that no desert map or tileset existed at all,
  which was the cleanest statement of that out-of-scope list and could only be
  true once. What outlives it is the invariant underneath: the cutscene still
  hands back to the title with the save pointing at the cabin, and every
  checkpoint on a desert map is gated behind the crossing flag it sets.

- Added the desert orc, which is the `UndeadEnemy` architecture with its dial
  moved rather than a new class: speed 22 against the zombie's 18 and the
  skeleton's 25, because the phase document says *slightly* faster, and 11
  scratches against the zombie's 8. Its sprite is built to the zombie's
  silhouette so the two read as the same kind of threat, and coloured against
  it -- leather and sun-bleached wrap over grey-green, a heavy jaw, tusks --
  so they never read as the same creature. The tests compare it to the zombie
  rather than to the numbers, so moving one end moves the other.
- Added `desert_orc_camp`, 64x48, north of the hub. Brown rock closes the
  north and west in an uneven front several tiles deep, and the only reachable
  map edge is the five-tile way back south; the fronts wander, because a rock
  edge ruled straight reads as a border drawn round the map rather than as the
  back of a canyon. Ten scratchable sacks and four burnt-out fire rings stand
  among seven orcs, and the ground inside the threshold is kept clear of both
  -- an orc in the doorway is a toll, not an encounter.
- The sacks are the Waterdeep pantry's own, by prop rather than by
  resemblance: a new tile character with `prop="grain_sack"` and sand
  underneath it, which is all `under` is for. The whole break-spill-clear
  lifecycle came with it for free.
- The fire rings started as four solid tiles round an empty middle and read as
  four crates standing in a diamond. They are one `camp_ash` tile now --
  stones round an ash bed with two burnt log ends -- because at sixteen pixels
  a fire is a thing, not a formation.
- The hub's north gap became a door. Because the four gaps were cut to shape
  in the previous session, wiring this one added markers and a return
  checkpoint rather than moving anything, which is what that decision was for.

- Added `desert_oasis`, 56x44, west of the hub, using the water, turf and palm
  rows the sheet already carried. No enemies at all, ten tufts of the
  established cigarette grass, and a pool small enough to put your back to --
  drawn at twice the size it filled two screens and read as a lake, where the
  phase document is asking for something you find at the end of a walk.
- It is a dead end closed three ways, and only two of them are walls: rock
  north and west, the Astral Sea along the south. That makes "sealed" a
  different measurement here -- a plain solidity flood calls the map wide open
  southward, because the Sea does not stop Chuck, it kills him. The test
  floods over walkable-and-survivable ground instead, and the only edge it
  reaches is the five-tile way back east.
- The palm canopy needed two fixes to work at all. Its tile was authored with
  neither `under` nor `overhead`, so it was walkable, blank, and drew no palm;
  and placed as single tiles the fronds read as bushes drawn on top of Chuck,
  because an overhead layer has no trunk beneath it. They are 2x2 clumps now,
  darkened so they do not disappear into the turf they shade, and a test
  stands Chuck under one and checks the pixels above him rather than trusting
  the tile table.

- Added `desert_undead_ruins`, 60x52, south of the hub: one building with an
  outer wall, cross-wall rooms, and a courtyard with the chest in the middle
  of it, rather than more scattered rubble. The hub already has six broken
  rectangles a player walks past, so this map only earns its place by being
  legibly somebody's building -- four intact corners, five doorways, an inside
  you can get into. Ten skeletons patrol it, unchanged from the Chult
  implementation. The Astral Sea closes the west and south as the document
  specifies.
- The chest is the sea captain's, and that took a small generalisation to be
  safe. `CaptainChest` carried its two progress flags as class attributes, so
  a second chest keyed to the same pair would have opened itself the instant
  the captain's was opened and paid out one carton between them. The flags are
  per instance now, the captain's remain the defaults, and the carton it drops
  banks whichever collection flag its own chest names. A test opens the desert
  chest and asserts the captain's is still shut.
- The hub's south gap became its third door. East keeps its shape and stays
  unwired, because it is the way forward and the map must not say so.

- Added the `collided` tileset, which everything east of the hub draws with.
  It is the desert plus whatever has fallen into it, and it grows a row per
  intruding world as the traversal needs them; DESERT itself stays fixed so
  the opening region's five maps cannot be disturbed by later work. Every row
  is rendered by the generator function that owns it -- the desert rows by the
  desert generator, the city rows by the city generator -- and a test compares
  the finished sheets pixel for pixel. A fragment of the modern city has to
  *be* the modern city, and the failure mode of redrawing one from memory is
  not a crash, it is a lookalike drifting a shade at a time until the player
  no longer recognises what they are standing on.
- Added `desert_east_1`, 68x48. Over 80% of it is desert ground and about 3%
  is intrusion, held as proportions so every later map in the sequence has a
  number to exceed. The one wrong thing in it is a slab of rain-dark city road
  with its lane line, lying in a tear of Astral Sea -- drawn with the same
  characters that draw a road in the city, so a map author cannot accidentally
  author a different one.
- The tear runs rim to rim and the road is the only way over it, which is
  proved by taking the road away: with the asphalt walkable the far half of
  the map is reachable and with it solid nothing over there is. The first pass
  tapered the tear short of both ends, leaving walkable sand round it, and the
  map claimed a crossing it did not have.
- The hub's fourth gap became its fourth door. All four now lead somewhere,
  and a test holds them to the same width, the same offset and the same
  terrain in front of each -- this is the point at which east could quietly
  start looking special, and it must not.

- Added `desert_east_2`, 72x52: the collision's second step. A wedge of Chult
  jungle -- the real jungle, with its stream still running -- pushed into the
  northern half, with the temple's snakes in the cover, and the city road
  returning as debris rather than as a bridge. Two worlds instead of one, and
  eight times as much of the map given over to them.
- The escalation is now measured as a comparison rather than a threshold. A
  number chosen today is a number a later map has to be tuned around; "more
  than the map before it, from more worlds than the map before it" is the
  property the phase document actually asks for and it keeps holding as the
  sequence grows. Every map added east should extend the same comparison.
- The sheet's provenance check moved into `test_phase13_collided_tileset`,
  which now owns it for every row and fails if a new row is added without
  naming the world it came from. It was in east 1's suite; it is a property
  of the sheet, and by the second world it was already being duplicated.
- The jungle's density pattern took three attempts, and the second failure was
  much worse than it looked. `(ax + by) % n` is constant along parallel lines,
  so the growth came out striped -- horizontally the first time, diagonally the
  second. The diagonal version left its open tiles touching only at their
  corners, and Chuck walks on edges, so the jungle had no way through it at
  all while looking perfectly plausible in a screenshot. It is summed sines
  now, and a test floods the open ground to prove it is one connected mass.
- The map does not block: the wedge stops halfway down, so the southern sand
  runs clear from door to door. I claimed that, then talked myself out of it
  and rewrote the map's docstring to say the opposite, then measured it -- the
  original claim was right. The test now proves both halves separately: with
  every foreign tile made solid the far door is still reachable, and the open
  ground inside the growth is still one piece.

- Added `desert_east_3`: a mass of Feywild filling the middle of the map,
  with its own ragged coast, glow pools, pollen and redcaps in it. A third of
  the ground is somebody else's. The desert still runs round it, so the player
  may decline -- but the fragment is a place now rather than a patch, and the
  Feywild is the right world for that step because it is the only one Chuck
  has visited that is not a shade of brown.
- Added `desert_east_4`: a slab of Phlegethos from rim to rim, with three
  wandering lava channels and fords across them. This is the first map east
  that cannot be walked past. The phase document's "lava hazards where Hell
  fragments appear" needed no new system at all -- `≋` has been a fall hazard
  since Phlegethos and stays one here -- and Hell's devils needed no new
  marker, because Phlegethos already authored one per facing standing on
  basalt, which is exactly what its fragment is made of.
- Escalation is now measured across the whole run rather than pairwise. East 2
  used to compare itself with east 1; with four maps that means every new map
  edits the file before it, so the comparison moved into one place that walks
  the sequence. It also had to change shape: the maps' worlds are not nested,
  because each has one big fragment that gives it its character plus scraps of
  the ones met before. What escalates is how many different places are
  arriving at once -- one, two, three, four.
- Those scraps were added because the test caught the maps reading as clean
  single-world overlays. A map with one fragment on it is an overlay; the
  collision is supposed to be getting messier.

- Added `desert_east_5`: the first fragment of somewhere Chuck has never
  been. A castle courtyard -- swept flagstone, ashlar walls, gated on four
  sides -- with armoured knights in it, plus a length of the ship's deck out
  on the sand. It is deliberately *kept* rather than ruined: the region has
  three kinds of fallen-down stone in it already and a broken castle would
  read as a fourth, so the wall is unbroken except at its gates and a test
  holds it to that.
- It is also not Waterdeep's castle. The docks sheet has had a `castle_wall`
  row since Phase 1 -- the backdrop behind the port -- and the phase document
  asks for somewhere clearly distinct from the docks, so the new rows are
  named `courtyard_*` and drawn cold and grey against the docks' warm keep
  stone. A test asserts the two rows stay separate.
- The provenance rule gained its one legitimate exception. Every row on the
  collided sheet is rendered by the generator that owns it and checked pixel
  for pixel; the courtyard has no owner, because there is no medieval map to
  import from. Those rows name COLLIDED as their source and skip the
  comparison, which is honest rather than a loophole: the reason the others
  are checked is that two copies of a picture drift apart, and these have one.
- The knight is `UndeadEnemy` again, with the dial pushed the other way from
  the orc's: the slowest and by some distance the toughest of the four, which
  is what armour is for. Its sprite is the only pursuer in the game with no
  face -- the others are read by theirs, and this one by not having one.
- East 5 is also the first map to hold two hazards in the same place, which is
  the document's "familiar systems in new combinations": an Astral tear with
  Hell's lava running into it. The test checks they are *adjacent*, because
  two hazards at opposite corners of a map is a list rather than a combination.

- Every fragment east now has a torn seam. A piece of another world with a
  clean boundary reads as having been *laid on* the sand, which is the wrong
  impression entirely -- these collided, and the game already has a language
  for reality coming apart. A shared helper frays the seam between each
  fragment and the desert with Astral Sea, and all six eastern maps use it.
- It took two goes. Taking roughly one seam tile in three, evenly, gives a
  dashed line: every fragment came out neatly outlined in Astral Sea, which
  reads as somebody having drawn round it. The tearing is a low-frequency
  function of position now, so whole stretches of a boundary are ripped
  through and others simply touch. The test measures run length rather than
  counting tiles, because an outline and a fray have the same tile count.
- Added `desert_east_6`: a frozen shelf with a cracked pool in it, and it
  actually snows -- but only over the snow. `SnowFall` masks each flake
  against the ground it is currently over, so the weather stops exactly where
  the fragment does, which turns out to be the clearest possible way of
  showing a player what they are looking at. It needs no list of snowy maps
  either: any map with snow tiles gets the weather.
- Two things had to change for the snow to read. Most flakes are culled by the
  mask, so the count that looks like weather in the abstract came out as a
  dusting; and lying snow at near-white made white flakes invisible, so the
  ground is a pale blue-grey now, which is what overcast snow is anyway.
- Added the blue dragon, the phase's one permitted new system. It is weather
  with a temper rather than an enemy: no health, no pursuit, no scratches, no
  ending. It breathes down a fixed lane for three quarters of a second in
  every four and a bit, with a warning that lights exactly the ground the bolt
  will take -- a telegraph that does not match its strike is worse than none.
  The tests pin what it must *not* have, because that is what a later edit
  adds back.

- A second art pass over the opening region, from a rock-cliff and a
  desert-ruin reference. The canyon rock was drawn as horizontal beds and had
  large flat areas in it; it is now broken into chunks taller than they are
  wide, grained in both directions from its own value everywhere, with one
  deep fissure that enters the top edge and leaves the bottom edge at the same
  x in every variant, so it chains unbroken down a whole cliff. That single
  constant is the whole trick: a tile's variant comes from its position and
  changes row to row, so anything drawn at a different x per variant stops
  dead at every tile boundary.
- It took three goes and both failures are worth keeping. A fissure every five
  pixels -- which is what the reference looks like at its own scale -- came
  back as wickerwork: at sixteen pixels a fin has to be most of a tile wide or
  the eye reads the repetition before it reads the rock. Then chunk faces
  drawn from the full palette read as crazy paving, because a strong value
  step between two touching shapes is a boundary, and a boundary round every
  chunk is a mosaic. The faces are three near-neighbour values now, and no
  highlight or shadow is ever drawn on the tile's own border -- an edge there
  is an edge along every seam in the sheet.
- Added the region's standing props, which is the layer the tileset cannot
  carry: a ruin reads as ruined because of what fell off it, and a column is
  three tiles tall, a fallen one two tiles long, and neither repeats. Broken
  columns at three heights, fallen ones in two or three drums, and heaps of
  cut blocks, each with a lit top face -- flat, they were glyphs. The hub and
  the undead ruins are dressed by one shared helper, because the hub's
  scattered rectangles are supposed to be fragments of the building south of
  them and two dressing rules would make them two kinds of place.
- The rule is about where, not what: columns at the corners where the load
  was, blocks outside the wall they came off, one column down full length per
  building. That is tested against the helper on a blank sheet of sand rather
  than by counting blocks on the finished maps -- the undead ruins' courtyard
  shares a centre with the building around it, so everything the courtyard
  throws off lands inside the outer wall and no count taken there can tell
  thrown-clear from tidied-away.
- The oasis has palm trees. It only ever had canopy tiles -- overhead shade
  drawn above Chuck -- authored as four clumps, three of which landed on sand
  instead of turf and were silently dropped, so what the map actually had was
  two lonely tiles of shade with nothing casting them. Nine palms now stand on
  a ring round the pool with their crowns written into the overhead layer
  immediately above them. Placed two tiles higher, as they were first, the
  shade came out as a green blob floating over each tree: an overhead tile is
  only shade if it lands where the thing casting it is.
- The camp's fires are pits rather than tiles. One sixteen-pixel square made
  the ring of stones three pixels of rock, which is why they read as pots; the
  ring is a prop wider than the rat looking at it now, standing on its own
  patch of scorched ground several tiles across. The scorch is walkable -- the
  fire used to be the wall, and it is the pit that is solid now.
- The orcs carry battle axes. Colour and a heavy jaw are four pixels of
  information; a shape held out past the silhouette is read across a room. The
  axe is drawn last, over the arm holding it, and its head is at chest height:
  carried any higher it lands level with the orc's own head and the two merge
  into a hat. Which way the blade faces is decided from the butt of the haft,
  because the head is on the left in two facings and the right in the third --
  drawn one way round for all three, two of them showed the blunt back of the
  axe at the only part of the frame the player can see.

- The frozen world has one dragon now, and it is the biggest thing in the
  game. There were two of them at 48x34, drawn in code out of about a dozen
  polygons -- the right size for a hazard marker and the wrong size for a
  dragon, where the wing was a triangle and the head an eight-pixel
  rectangle. Two of a thing is a species; one of a thing is *the* dragon, and
  the map only has room for one creature that cannot be fought.
- It is a sprite now at 128x96: eight tiles by six, nearly twice the massive
  Chult dinosaur and about nine times Chuck's height, which is roughly the
  real ratio between a one-foot rat and a dragon. The size is tested as a
  comparison against the dinosaur's own frame rather than against a number,
  so "biggest" stays a claim about the game rather than a constant.
- Six frames: four of wing beat and two of the breath, which is a separate
  pose rather than the idle with a mouth pasted on -- head down, neck
  forward, jaw open, throat lit. The jaw opens part way through the wind-up,
  because the lane lighting up is on the ground and a player with a dragon on
  screen is not looking at the ground.
- Two drawing notes worth keeping. The open mouth first came back as a zip
  fastener: teeth drawn to the same line from both jaws close the gap between
  them, and what says "open" is the dark between the rows rather than the
  teeth. And the tail read as a shadow cast by the haunch until it was given
  a lit edge along its top and run out past the hind leg to a fin.
- The lane grew with the animal -- fourteen tiles of reach and four of width
  -- and is aimed at the breathing pose's mouth rather than the idle one's.
  The strike is one fixed rectangle in every stage, so where the two poses
  disagree it should be the idle head that is slightly off, never the one the
  bolt actually leaves.

- Everything east of the hub is dressed now. Each map had a piece of another
  world in it and that piece was a rectangle of somebody else's ground
  colour, which is enough to say "this is not the desert" and nowhere near
  enough to say "this is Chult". A world is recognised by what is on it, so
  Chult's fragments carry Chult's own trees and bushes, the Feywild's carry
  its grove trees, shrubs and mushrooms, Phlegethos's carry its basalt
  rubble, and the ruins east carry the same fallen columns and spilled blocks
  the hub's do.
- Every prop is the one its own region uses at home rather than a
  desert-styled lookalike, and the test compares them against the character
  that region spells them with. They needed characters of their own only
  because the collided maps had to rename the *ground*: Chult spells its
  jungle "." and "#" and the desert had already claimed both, so the fragment
  kept its art and took new letters.
- One shared placement rule across all six maps, with one property that has
  to hold: no prop may ever close a route. Every one of them is solid and the
  fourth map's basalt slab is the only crossing there is, so a prop is only
  planted on walkable ground where all four sides of the tile are standable.
  That is not a chokepoint by construction, and it is measured on the
  finished maps rather than trusted to the rule.
- Three things went wrong and each was invisible in the source. The rule was
  first written as "the whole three-by-three is the same ground", which is
  safe and far too strict -- the small scraps are three or four tiles across
  and never have a uniform middle, so three maps came back with an undressed
  piece of Chult on them. The pass also ran before the rim was drawn and
  before the scraps had landed, so it planted trees against a border that did
  not exist yet and skipped fragments that did not either. And where the
  clumping ran high across a whole stand, the spacing rule was the only thing
  left deciding, and minimum-spacing packing is a lattice: a bank of bushes
  came back as a pegboard, fixed with a fine-grained term on top of the
  clumping.
- A fragment is dressed at the density it can afford. A map's main fragment
  is hundreds of tiles and wants thinning; the scraps of the worlds it met
  further back are a dozen or two, and at the density the big one wants a
  scrap that size draws nothing at all.
- Phlegethos's lava fall is on the fourth map, off the northern cliff, and it
  ends in the Astral Sea rather than in a river. That distinction is the
  whole reason it is there: a fall feeding a channel is a fourth channel with
  a nicer top, where a fall pouring into a hole in reality says what the
  region is about -- the lava is running out of the world rather than through
  it. Tested as all three of small, touching the Sea, and reaching neither
  rim, since the channels beside it do reach both.
- The fifth map's lava banks went from one tile wide to two. Every basalt
  tile on that map touched lava, which is a stripe rather than a place: there
  was nowhere on it to put anything down, and the rubble that came through
  with it had nowhere to lie.

- Added `desert_east_7`, where the collision stops being tidy. Every map
  before it is the desert with something in it; this one has nine pieces of
  world on it and no majority -- the largest cell is under a third of the map
  and the smallest is still worth walking into. The phase document asks for
  the later maps to be heavily fragmented and geographically impossible, and
  both of those turn out to be measurable: fragmented as the absence of a
  majority, impossible as *adjacency*.
- The cells come from scattered points rather than authored rectangles, so
  their borders fall out of the arithmetic. Rectangles would have given
  straight seams, and a straight seam between two worlds reads as a wall
  somebody built. The distance is measured with a wobble on it so the borders
  bulge and bite instead of being the exact bisectors.
- Two of the nine are Chult and they are in opposite corners; two are desert
  and they never touch. That is the impossible part stated plainly, and it is
  what the test measures rather than "the worlds are present": snow against a
  ship's deck, a courtyard against Hell, and the same world twice in places
  that are nowhere near each other.
- There is no sand here to fray against, so the Astral Sea frays between the
  worlds themselves -- which means most of the map's structure is holes. The
  route is therefore guaranteed by construction rather than found: a corridor
  is walked from the west gap to the east before anything is torn, and every
  tile of it is protected from tearing afterwards. It is invisible, because
  it is made of whatever world it happens to be crossing; all that marks it
  is that the ground there was not taken away.
- Six kinds of enemy on one map, each standing in the world it belongs to:
  snakes in the jungle, redcaps in the Feywild, spined devils on the basalt,
  knights on the courtyard, skeletons in the ruins and orcs on the sand. None
  of them is new, which is the document's "final mechanical remix" -- all of
  them being here at once is the only thing this map does that no earlier one
  does. They stand four tiles clear of the corridor: an enemy in the only way
  through is a toll rather than an encounter.
- The ship's deck got barrels and crates, its own from the ship. It is the
  largest single cell on the map and bare planking is a floor with nothing to
  say it was ever at sea.
- One more instance of the modular trap, in the shared dressing helper: the
  prop variant was picked with `(x * 7 + y * 13) % len(props)`, and any linear
  form taken modulo two is the parity of x + y -- so a ground with two props
  laid them out as a checkerboard, and the spacing rule on top of that picked
  all of one and none of the other. Hashed now.
- The sixth map's east gap is a door rather than open sand, and the seventh's
  east edge is still rim. Same rule as the hub's four gaps: the neighbour
  arrives as a marker, not as a reshaping.

- Added `desert_east_8`, where the ground has mostly gone. The seventh map is
  nine worlds touching each other; this is the same worlds not touching. Two
  thirds of it is Astral Sea, a fifth of it can be reached, and what is left
  is islands joined by causeways two tiles wide.
- The escalation is structural rather than another count of fragments. Up to
  here "further gone" has meant more of somewhere else and less desert; here
  it means there is less of *anything*, and every walk across the map is a
  walk along a ledge with the Sea on both sides. The document lists narrow
  routes and Astral Sea fall hazards among the things to reuse; this is both
  at once and nothing else. Its share of Sea is tested against every earlier
  map rather than against a number, so it cannot quietly be tuned back down
  to merely torn.
- Two islands have no causeway at all. They are drawn, lit, weathered and
  impossible to stand on -- the document's "walls and towers visible through
  Astral Sea sections" taken at its word. That one is asserted as a thing the
  map must fail to do, because the natural drift of a later edit is to join
  them up: an island with no bridge looks like an oversight rather than the
  point.
- The causeways change material halfway. A bridge from the jungle to the
  courtyard is jungle at one end and flagstone at the other, because nobody
  built it -- it is what happens to be left of the ground between two things
  that were never near each other.
- Measuring "narrow" took three goes and the failures are the interesting
  part. Runs along x and y call a two-wide diagonal ledge four wide, because
  a two-wide diagonal is a staircase; and a tile at a landing has island on
  seven sides and is not a ledge in any sense a player would recognise. What
  it finally measures is the thing the word actually means: every tile out
  over the Sea has open Sea within a step of it, so there is nowhere to step
  aside to.
- The render check took three goes too, and for a reason worth keeping: half
  these islands are dark, so brightness cannot tell them from the Sea, and
  the Sea is drawn with a starfield, so it has *more* colours on screen than
  a courtyard does. It asserts that four places on the map draw differently
  from each other, which is what a missing tileset row would take away.
- The seventh map's east gap became a door. It was cut as rim with the
  corridor already running to it, so adding the neighbour added a marker and
  a gap and moved nothing -- and its test now checks that the two doors match
  each other exactly rather than that the east one is still closed.

- Chuck has reached the trio. `desert_trio` is the arena for the final
  encounter: the three of them holding a spot in front of the rift the wizard
  is opening, most of the adventure's enemies pressing in, and Chuck arriving
  in the middle of it for the third and last time.
- The room answers two instructions that pull against each other. The
  document wants the most chaotic version of an encounter the player has
  survived twice, and in the same breath says not to spend readability on
  spectacle. So the chaos is underfoot and the danger is above it: the floor
  is nine worlds jammed together with no desert between them, and under two
  per cent of the arena is solid. Cover would turn a fight about movement
  into a fight about hiding, which is not a fight Chuck is allowed to win.
- The wizard is *working* rather than fighting, and that is what keeps a room
  this crowded fair. Everything he throws goes east into the rift, and east
  of the heroes there is no ground at all -- so the biggest, loudest thing on
  screen is by construction the one thing that cannot hurt the player. The
  rift comes all the way in to him across the band his work travels down;
  left to the bow of its edge alone there was a column of walkable floor one
  tile wide in the lane, which is exactly the sort of gap a fight finds.
- Everything reuses the established battle architecture: the same three
  actors, the same projectile path, the same entrance-dialogue cut to the
  tableau. A player has met these three twice and is meant to recognise them,
  and a third pair of sprites would have cost that with nothing failing. What
  is new is one choreography -- faster and wider than the sanctum's, checked
  against it rather than against numbers of its own.
- The three of them stand six tiles apart, not eighteen. The camera cuts to
  the group for their lines and lifts to keep their feet off the dialogue
  panel, so the span that fits in one frame is well under a screen's height:
  spread down the map, as they were first, the fighter was simply not in the
  shot.
- The final encounter is a development entry by name, which the phase
  document asks for: it is the far end of a very long walk, and testing it
  from the hub is not testing it.

- The encounter talks its way through the fight. All four of the document's
  later exchanges play on a clock rather than on trigger volumes -- Chuck is
  never asked to walk anywhere to advance it, because walking anywhere in
  that room is not something he can reliably do. Fifteen to seventeen
  seconds of surviving between each pair, which is the instruction to keep
  gameplay moving between dialogue moments taken literally: four beats back
  to back would make the room a cutscene with fighting in the gaps.
- "The environment should become increasingly unstable around Chuck" is the
  other instruction, and here it means the rift wins ground. From the
  midpoint on, every beat takes another column: the floor immediately west of
  the tear breaks through to Astral Sea, which is the sanctum breach's exact
  mechanism applied to a moving edge instead of a fixed band. The space
  Chuck has to dodge in shrinks each time the heroes speak.
- The edge is ragged, so what gets taken is *found* rather than computed --
  for each row, walk west from the map's east side to the first tile that is
  not already Sea. A column index would have cut a straight line down a torn
  edge, which is the one thing the whole region has been avoiding.
- Two things it must never do, both tested rather than trusted, because both
  look like bugs when they go wrong and like nothing when they go right: it
  never opens under Chuck, and it never takes the footing out from under the
  three holding it. Their rows simply stop advancing, so by the last beat
  they are standing on spits of sand with the Sea all round them -- which is
  the right picture anyway.
- Dying heals the arena and puts the conversation back to the start, the same
  way the sanctum's breach re-arms. A player who dies to the last beat should
  get the encounter, not the wreckage of their previous attempt with the
  script already spent.

- The final collision sequence. When the wizard says "Good enough" the desert
  stops being a desert: large sections of it repaint to another world's floor
  every couple of seconds, and then faster, down to a section every half
  second. That is the document's own description -- overwhelmed by fragments
  of locations from throughout the game, in large, rapidly changing sections.
- It comes with the document's own warning attached, and the warning is what
  made it buildable: readability must not be spent on spectacle. So the churn
  only ever writes *floors*. It cannot kill Chuck, cannot block him, and
  cannot take a route away; what changes is what he is standing on, nine or
  more tiles at a time. The arena's rule was that the worlds are underfoot
  and the danger is above them, and the ending is that rule at its limit.
- That is one claim with three consequences and all three are measured
  rather than trusted, because the failure mode is not a crash -- it is a
  section of lava arriving under a player who had nowhere to be. Every tile
  it wrote is checked to be walkable; everything that is not a floor (the
  rift, the lava veins, the rim, the heroes' footing) is checked to be
  untouched; and the set of tiles reachable from the arrival is checked to be
  identical before and after.
- Sections come from a fixed walk over the map rather than at random. A map
  is generated once and read many times, and a sequence that differs per run
  is a sequence nobody can tell is working -- including whoever has to decide
  whether the last change improved it.
- Each arriving section is outlined for a third of a second rather than
  filled. Filled, the flash washed the thing it was announcing, and what a
  player most needs to keep track of in that room is where their own feet
  are.

- Phase 13 has an ending. The resolution plays over the collision -- the
  heroes realising it is taking, and then realising what else is caught in
  it -- and "Where he belongs!" is the trigger. The worlds come apart, the
  blast carries Chuck out, and he lands on the Waterdeep docks.
- The trigger waits for the conversation to close rather than firing on the
  line, which is the sanctum Fireball's own shape: fired on the line, the
  sentence gets cut off by its own consequence.
- The rift stops taking ground once the collision starts. From "It's working"
  onward the heroes are *closing* it, and a room that kept eating the floor
  while they said so would be the ground arguing with the dialogue.
- The return cutscene is the last of the game's repeated world-transition
  sequences and quotes all of them: the table portal's whiteout, the fall to
  Chult seen sideways, the same Astral Sea that has been the seam of every
  crossing since the pantry. What is new is the direction -- every other one
  took him somewhere, and this one takes him back.
- The fragments separating had to *leave* rather than be busy. Each world is
  a band, and they stop coming one at a time until nothing is rushing at all;
  what is left when the noise stops is stone, water and gulls. All of them
  ending together would be an effect being switched off rather than a thing
  ending.
- It ends at the title with the crossing recorded and nothing written. The
  finale is a phase that does not exist yet, so there is nowhere to hand to:
  this is the same honest ending the desert arrival had before Phase 13 was
  built, and its test says so in a way that fails when the finale arrives.
- One bug worth keeping, because it cost nothing to write and showed nothing
  at all: the two-second fade into the quay was written as "before the docks
  arrive", which is true from the first frame -- so the whole twelve-second
  rush played under full white. There is a test pinned on it now.

- The region has one piece of music now, and the arrival cutscene is part of
  it. The cutscene used to open with a cue of its own and then hand to the
  theme, which is two pieces of music with a join in them; it now starts the
  theme itself and the map picks it up. The join is gone because there is
  nothing to join -- the audio system treats a repeat request for the track it
  is already playing as a no-op, so the tune simply carries on under the scene
  change. The test for that compares the two calls rather than the sound,
  because the loop flag being different is the only way it can quietly fail.
- `desert.wav` grew from 48 to 120 seconds for that reason. At seventy-five it
  was a map theme with a separate cue in front of it; at two minutes it is one
  piece that can open a scene, carry a walk, and turn over without announcing
  its own length.
- Two thirds of it is now D Phrygian dominant over a held drone -- the flat
  second with the major third above it, which is the interval this kind of
  music is actually recognised by. The frame at both ends stays in D Dorian,
  which is where the rest of the region's music lives and what the arrival cue
  was written in, so the two halves share D and A and the joins are the same
  room lit differently rather than modulations. Nothing was transposed.
- The deserty part adds a drone and takes the bass off its walk; it does not
  add drums. Piling on percussion is the cheap version of that instruction and
  it would have made the middle of the region sound like adventure rather than
  heat. What changes instead is that the harmony stops moving and the reed
  ornaments instead of stating, which is the difference between a tune played
  in a mode and one that belongs to it. A test pins the kit at two voices.
- Added `desert_trio.wav` for the final map: the desert theme and the fall to
  Chult at once. It works because they were already in the same key -- D
  Dorian against D minor, same tonic chord, one note apart. So the arrangement
  *is* that one note: eight bars of the desert as the player has had it for
  eight maps, and then the sixth drops and the fall has arrived without
  anything else changing. The Eb follows eight bars later, which is the fall's
  other tell and has meant "this is going badly" since the sewer.
- It reads as the fall because it brings the fall's own things -- its pulse,
  its kit, its bells, its wrong note -- and stays the desert's because the
  arpeggio underneath is the desert's arpeggio, unchanged, and the reed still
  answers in the gaps. The heroic part is the one trick available on this
  synth: the fall's hook, which has only ever gone past in eighths, stated on
  brass in half time with timpani under it. Same notes, four times the length.
- 104 BPM, between the desert's 96 and the fall's 120, so neither set of
  material is rushed or dragged into the other's. A test asserts the ordering
  rather than the number.
- It is the only map east of the hub where the music changes at all, which is
  what makes it land; a test walks all twelve desert maps to say so.
- The old `desert_arrival.wav` cue is not orphaned. The arrival cutscene no
  longer plays it, but the return-to-Waterdeep cutscene does -- so the tune
  from Chuck's arrival is what plays as he leaves, which is a better place for
  it than the thirty seconds it used to occupy.
- Phase 12's `test_the_desert_has_a_cue_of_its_own_...` was rewritten rather
  than deleted. Its claim was correct while Phase 12 was the last thing built:
  with nothing playable on the far side, a one-shot sized to the scene was all
  the crossing could have. What outlives it is the part that still matters --
  every cue the scene fires names a file that is really there, and the three
  quiet noises are texture rather than events -- plus the new statement that
  the scene starts the region's theme looping and asks for nothing else. It
  still checks `desert_arrival.wav` itself, now against the length of the
  sequence that owns it.

- The final encounter has a horde in it. The complaint was theatrical and
  exact: the ranger was spinning on the spot throwing arrows in every
  direction at nothing at all. It was a fair hazard and an absurd tableau,
  and the phase document's own line about this encounter -- that the three of
  them "may also be fighting enemies or another threat" -- had never been
  taken up. Now orcs come at them in a continuous stream, out of the camp
  Chuck passed on his way into the region.
- The horde has not noticed Chuck and never does. Each orc charges the
  fighter or the ranger, chosen once at spawn as whichever it came in
  nearest, and nobody charges the wizard -- he is working, and a room where
  he had to defend himself is a room where the thing he is doing stops. What
  it costs Chuck is being in the way of it: they are bodies in the same
  floor, and running into one costs what running into any orc in this region
  costs. The room became a weave rather than a chase.
- The heroes kill in one. Her arrow drops an orc that takes eleven of
  Chuck's scratches, and the fighter's sword takes anything that gets past
  her -- because these are the people who do this for a living and the room
  has to look like it. His swing is reactive now rather than on a clock, and
  his arc goes all the way round him instead of only west, because this horde
  converges from three sides.
- Far fewer arrows, and the room is more dangerous for it. One aimed shot
  every three quarters of a second where the whirl threw three every fifth of
  one -- most of an order of magnitude fewer. A whirl is a pattern to stand
  outside of; a line drawn between a woman and whatever is nearest to her
  moves every time something dies, and it can be drawn straight through
  wherever Chuck is standing. The hazard stopped being weather and became
  traffic.
- Two failures worth keeping, because neither is visible in the source and
  both look like a worse fight rather than a bug. Half the first spawn ring
  put orcs beside a lava vein, and a greedy pursuer walks into one and stays
  there forever -- a dozen orcs standing in a field forty tiles from anybody,
  with the ranger dutifully shooting the nearest of them. That is the
  "attacking nothing" problem again in a new costume, and it is why every
  approach is now simulated to the line before it is written down.
- The second was worse and needed the arena changed. The rift takes a column
  of ground on every beat and the Astral cracks grow with it, so by the
  fourth exchange each hero was standing on a single tile at the end of a
  spur one tile wide -- and nothing with a body can walk down a corridor one
  tile wide. The fighter's sword quietly stopped being able to hit anything
  about a minute in. The rift now spares each hero's whole 3x3, which the
  generator already clears to plain desert, so the three of them end up on a
  shelf jutting into the tear instead of on islands. That is a better picture
  anyway: they are *holding* this, and holding it needs somewhere to stand.
- The orcs go round what they cannot go through. Every other pursuer in the
  game walks straight at what it wants, which is fine in an open room; this
  one is neither open nor stationary. So they try the direct line every
  frame, and follow the obstacle when it is blocked, sticking to the same way
  round for a moment rather than reconsidering every frame -- which is how a
  thing ends up vibrating in a corner. The subtlety that made the first
  attempt fail: `move_and_collide` resolves the axes separately, so a
  diagonal charge into a wall still slides a fraction of a pixel and still
  returns a new position. "Did it move?" is always yes. The question that
  separates walking from grinding is "did it get closer?".
- The approaches come from the west and the south, and none from the north
  rim, which was measured rather than chosen. The crack running from (48, 14)
  welds onto the rift and leaves a funnel that narrows to one tile and stops,
  so anything walking south down the map's east side ends up in a cul-de-sac
  four tiles from the fighter with no way to know it should have gone round.
- What the room plays like now: two converging currents with a seam between
  them, arrows crossing that seam whenever the ranger's nearest target is on
  the far side, and the fighter's arc at the end of it. Standing on a
  converging lane is punished hard; the middle is a road, and it leads to the
  one lane in the room that has always been lethal.

- A red dragon crosses the arena during the collision. It is the blue
  dragon's contract in motion: same construction, same palette discipline,
  no health, nothing to fight, nothing that stops it coming. The difference
  is that the blue one is a fixed thing that is sometimes lethal, and this
  one is always lethal and never in the same place twice.
- It is the fourth thing pressing Chuck in that room and it had to be a
  different *kind* of thing from the other three or it would only have been
  more of them. The arrows come from a fixed point, the horde walks fixed
  courses, the churn repaints the floor without ever making it dangerous --
  all three are pressure he reads around himself. A stripe of fire crossing
  the arena at whatever row he is standing on is the one kind he has to read
  about himself.
- It aims at him once and then commits. The row comes from wherever he is
  standing when the pass begins and is fixed for the whole crossing, so a
  player who stays put is hit and a player who moves is not -- which is the
  difference between a dodge and a chase, and the approach becomes a promise
  about where the fire will be rather than a thing changing its mind.
- That aim is also what closed the room's last safe pocket. The horde's two
  streams converge on the fighter and the ranger and leave a seam between
  them, so the middle row of the arena was a road with nobody on it, out of
  the wizard's lane and off every orc's course. The dragon is the one hazard
  that follows him into it.
- The trail glows before it burns. Three tiles is wider than a one-foot rat
  steps out of on reflex, so the ground is warm and harmless for a full
  second before it catches, and then lethal for two, and then embers. Fire
  that lit the instant the dragon arrived would be a hazard that hits before
  it can be read.
- It writes nothing to the map. The rift takes ground and the churn repaints
  it; between them this arena already changes under the player faster than
  anything else in the game, and a third thing editing the floor would make
  it impossible to say what any given tile is. Nothing catches over the rift
  either -- a stripe painted across the Astral Sea would hide the one edge in
  the room that has always killed him.
- It does not care whose side anybody is on: orcs standing in it burn, which
  is most of what sells the thing as weather rather than as an attack aimed
  at the player.
- The sprite is drawn from above, and that is the one place it departs from
  the blue dragon. Everything else in this game is seen from a low side
  angle because everything else is standing on the same floor Chuck is. This
  one is not. Drawn in profile the wing sweeps through exactly the space the
  body and the tail occupy, so the bottom of every wingbeat came back as one
  flat red mass with a plank sticking out of it -- tail behind the membrane,
  legs behind the tail, nothing readable. From above nothing overlaps
  anything, and the beat is carried by how far out the wings reach.
- Twelve frames rather than the blue one's six: a wingbeat, and then the same
  wingbeat with the jaw open. Given the breath its own two-frame pose the way
  the blue dragon's has, the wings would stop mid-air for as long as it was
  breathing -- the exact moment a flying thing must not look paused.
- Two art failures worth keeping. The spine ridge drawn at any size larger
  than three pixels stopped being scales and became chevrons, so the animal
  came back with arrows printed down it. And the fire, drawn as rectangles,
  was three perfectly straight bands running the width of the arena: an
  orange flag rather than a fire, with an edge so clean it read as interface.
  Both layers now take their height from *position* rather than from the
  patch's index, so neighbouring patches share an edge and the stripe ripples
  along its length.
- One ordering bug behind that: drawn patch by patch, each patch's outer band
  painted over the previous one's bright core, and every tongue came back
  with its right half missing -- a row of arrowheads pointing the way the
  dragon had come. It is drawn layer by layer now.
- Two older tests changed rather than being deleted. `test_phase13_trio_beats`
  ran the room without holding Sanity up, which was fine while a player
  standing still could survive it; a passive player now burns partway through
  the fourth exchange and the conversation restarts from the top. That is
  correct, and it is the whole point of the dragon, and useless for a test
  about what gets said in what order.

- The arena closes from behind as well. Chuck arrives on the west rim and
  everything worth watching is twenty-five tiles east of him, which put an
  obvious exploit in the room -- and not a cowardly one, a *sensible* one:
  stand in the doorway, let the arrows and the horde and the dragon happen at
  a distance, and wait out the conversation. A room with a corner in it is
  not an encounter. It is a cutscene with a survival timer.
- So the Astral comes in from the west too. It starts after the first
  exchange, takes a column every 1.8 seconds, and has finished about when the
  collision begins -- so the squeeze and the climax are one event rather than
  two things happening at once. What is left is a band about a screen and a
  half across with the trio at one end of it.
- Where it stops is the horde's decision, not taste. The westmost cell orcs
  come in from is column 28, and a front that went past it would be a spawn
  ring inside the Sea -- a horde drowning on its way to the fight the squeeze
  exists to push him into. A test asserts the limit against the ring rather
  than against a number.
- It is the sanctum breach's fiction said again, and it takes the Ashtray
  with it: a save point left floating in the Astral Sea reads as a bug, and
  it is the one prop in that room a player would try to walk back to, which
  is exactly the walk this removes.
- It pushes him, and then it finishes. The rule everywhere else is that the
  Sea never opens where Chuck is standing -- right for the rift, which comes
  at him from in front, and wrong for a front coming from behind: the first
  version left a player who ignored forty-five seconds of visible Sea on a
  single tile with the fight thirty tiles away and nothing to do but wait for
  the dragon to find him. Three columns past him the front now takes his
  ground as well. Standing still is a death rather than a stalemate, which is
  both the better failure and the honest one.
- The edge is torn rather than ruled. Taking whole columns gave a perfectly
  straight vertical line sweeping the map, and a straight line does not read
  as the Astral Sea, it reads as the end of the level. Each row lags the
  front by its own fixed amount, from two sines -- not `row % n`, which is a
  repeating sawtooth and the same problem with a different tool.
- The music changes when the wizard finds it. `desert_dragon.wav`: the same
  trick a third time and one step further down. The desert is D Dorian; the
  mashup dropped the sixth and became D minor; this drops the second and
  becomes D Phrygian. So the Eb -- which has meant "this is going badly"
  since the sewer and arrives in the mashup as a wrong note pressing in -- is
  now simply the second degree of the scale. The wrong note has become the
  key, which is the shortest way to say the situation has stopped being
  recoverable and started being the situation.
- Everything else in it is what a boss theme is made of here: the desert's
  own arpeggio still running and at twice the rate, a square bass hammering
  eighths instead of walking, the fall's hook in quarter notes where the
  mashup states it in half time, an Ab that belongs to no key at all under
  the dragon's bars, and the full kit from bar one -- this piece does not
  build to anything, it is the thing that has already happened.
- 132 BPM, above both of its parents, and the loudest and densest thing in
  the phase (0.80 peak, 0.217 RMS against the mashup's 0.72 and 0.138). It
  starts on "Good enough" rather than on the dragon's first pass: that line
  cuts the camera to the three of them, and a hard change of music under a
  hard change of shot reads as one event. Two seconds later, when the animal
  appears at the edge of the arena, there is nothing on screen to hit.
- It is not in AREA_MUSIC, because it does not belong to a map -- it belongs
  to a moment. The room asks for it every frame once the collision starts,
  which is a no-op after the first, and asks for the map's own theme again on
  reset: the respawn rebuilds this arena in place rather than reloading the
  scene, so a player who died in the last thirty seconds would otherwise
  begin the encounter again with the music from the end of it.
- Six older tests changed rather than being deleted, all for one reason: they
  parked Chuck on the arrival tile for the whole encounter, which the front
  now takes about half a minute in. That kills him and restarts the
  conversation -- correct, and the entire point of the front, and useless for
  a test about what the rift does or what gets said in what order. Each now
  holds him somewhere the front does not reach, and the one that asserted the
  Sea never opens under him says where that rule is broken on purpose.

- The dragon's act is now most of the encounter rather than a coda. The last
  two exchanges went from eighteen and fourteen seconds to forty and
  thirty-two, and the gap is the point: up to there the room is a
  conversation with fighting in the gaps, and from there it is a fight with
  two lines in it. At the old lengths the dragon got two crossings and no
  time on the ground at all -- the whole back half went past before its own
  hazard had finished introducing itself.
- Every pass now stops part way across. It flies in laying its stripe, comes
  down in the arena, spits fire, climbs, and lays the rest of the stripe on
  its way out. It was every *second* pass at first, so the plain crossings
  would keep happening, and what that bought was two landings in the whole
  encounter -- one step of escalation and no curve. A landing pass is not an
  alternative to a crossing; it is a crossing with a stop in it. Four
  landings now, and both hazards every time.
- What it spits is balls of fire that roll along the floor, and they are a
  different *kind* of hazard from the stripe on purpose. The stripe is a line
  drawn once, across the whole room, that Chuck steps out of; the rolling
  fire is a handful of slow objects coming at him from one point, which he
  has to move between. One is a wall and the other is traffic, and having to
  switch between reading them is most of what makes the last minute feel like
  the last minute.
- They get worse every time it comes down: the fan is one ball wider (three
  to six), the balls are faster (56 to 92 px/s), and the volleys are closer
  together. The speed is the one that matters -- it starts below Chuck's own
  80 and ends above it, which is the moment outrunning the fire stops working
  and stepping through the gaps is all that is left. Measured rather than
  felt: a stationary Chuck takes eighteen hits across the act and a crude
  sidestepping one takes four.
- A ball costs less than the stripe. The stripe is a wall he chose to stand
  in; a ball is one of four things that came at him while he was dealing with
  the other three, and only one of those is avoidable at leisure.
- It lands short of him, on ground, inside the arena. All three were failures
  worth avoiding by construction: a landing on his own tile is a fan at
  point-blank range, which is not a dodge but an announcement; a landing on
  the Astral is a dragon standing on a hole with its fire dying as it leaves
  the mouth; and by the time it starts coming down the western half of that
  floor is gone, so "inside the map" and "on the floor" are no longer the
  same question. It walks out from the wanted column until it finds
  something to stand on.
- A landed dragon sorts with the room. In the air it draws over everything,
  because it is not on the floor at all and sorting it by its feet would put
  a flying dragon behind a waist-high rock. Down, it goes in the y-sorted
  pass with everything else that has feet -- otherwise eight tiles of red sit
  on top of Chuck for six seconds, which is the one thing this arena is not
  allowed to do.
- Four new sprite frames, and the silhouette is the whole of the difference.
  Landed, the wings fold back along the flanks, the legs come out from under
  it to carry weight they were not carrying a second ago, and the tail lies
  down instead of streaming. Without that the moment of touching the ground
  read as the animation stopping.
- One performance fix that will keep paying: the dragon hands the horde forty
  rectangles a frame once its rolling fire is up, and calling `cut_down` once
  per rectangle walked the whole horde forty times and rebuilt every hitbox
  on each walk. `cut_down_any` walks it once. (The 3.8ms frame I chased first
  turned out to be the music swap's one-off `mixer_music.load`, amortised
  into the average by a benchmark that started on the wrong frame.)

## Next logical task

- Continue Phase 14 on the shared docks map: add the non-explorable docked ship,
  fisherman, and increased ending-state market population without changing
  the quieter opening state or obstructing Chuck's established routes. The
  eastern fountain plaza follows as shared starting/ending geography.

## Superseded Phase 12 task

- Add the awakened table map's close-proximity `Enter planar portal?` YES/NO
  interaction. NO should close cleanly; YES should begin the short desert
  arrival cutscene through the established scene/fade architecture. Keep desert
  gameplay out of Phase 12.

- Added the authoritative Phase 12 contract for the Cabin. It begins
  after the recorded Douglas-fir crossing and contains exactly two peaceful
  playable maps: the nighttime cabin grounds (including the south porch) and the
  cabin interior. There are no enemies or environmental hazards.
- Archived Sean's authored layout, seven site/interior photographs, and the
  color-changing mushroom-light reference under
  `docs/design/references/tahuya-cabin/`, with an index distinguishing direct
  phase requirements from visual source material.
- Locked the phase around faithful real-place layout, a compact three-quarter
  exterior landmark with one reversible aligned south door, one
  shared-loader checkpoint per map, independently offset path lights, four
  exact strange entity dialogues, and the later-door-gated table-map portal.
- The phase ends at an input-locked desert-arrival handoff. Desert gameplay is
  reserved for Phase 13. The psychedelic, catchy, bass-driven cabin soundtrack
  is a major Phase 12 deliverable and should receive its own review pass.

## Latest implementation

- Increased the collided-world dressing around the Fractured Way bus stop
  from five to eleven Astral fragments. Every fragment remains off the paved
  approach, so Chuck can still stand beside and interact with the umbrella
  businessman without crossing a fall tile.
- Moved City Day 6's planar portal from the northern arrival room to the far
  southwest end of the shattered route, more than fifty tiles from spawn. The
  player now crosses the damaged plaza before discovering the phase exit.
- Replaced the square, thorn-like Douglas fir terrain with one human-scale
  80x80 oval portal prop. Twelve procedural frames rotate broad muted tie-dye
  fields through a predominantly gray interior, with a silver rim and layered
  blue, violet, rose, and green light projected onto the wet pavement.
- Reduced the Doug fir automatic choice zone from 3x2 tiles to the single tile
  at its threshold. Chuck can now approach closely enough to inspect the full
  animation before `Enter planar portal?` appears.
- Focused daytime-city, Doug fir handoff, and shared tileset tests pass; the
  portal's position, safe reachability, oval alpha silhouette, animated color
  field, projected light, and close-only prompt all have regression coverage.

- Removed the thin molten fissure from the Phlegethos fall cutscene's landing
  plane. Because that line was positioned relative to the rising ground
  surface, it appeared to slide in from the lower-left during approach. The
  foreground is now uninterrupted basalt; the distant volcano and all playable
  Phlegethos lava remain unchanged.

- Raised the authored City Sewer music trim from 1.55 to 1.65. At the standard
  0.6 music-stream level the cue now plays at 0.99, just below the mixer's
  ceiling, without changing the WAV master or the volumes of either city cue,
  the medieval sewer, sound effects, or any other region.

- Added the 76x48 Fractured Way immediately before the Phlegethos fortress
  fight. The reciprocal chain is now Rubble Pass -> Fractured Way -> Fortress
  Approach, while the existing fortress arrival name and fight trigger remain
  unchanged.
- A wide route meanders around 306 dark rubble pieces and three small lava
  ponds. Three flameskulls weave only above those ponds as environmental
  motion; the sole true enemy is a full-scale, slow Pit Fiend positioned
  beyond notice range from the required path so it is easy to avoid.
- A procedural modern bus shelter and the existing umbrella businessman form
  a reachable collided-world tableau with the exact `Ah! A rat!` dialogue.
  Eleven nearby Astral fragments establish the collision without fencing Chuck
  away from the NPC.
- Four one-tile Astral cross-bands form the only mandatory challenge and are
  cliff-backed so they cannot be walked around. The map has its own Ashtray
  and shared-loader `Phlegethos 5` checkpoint; Fortress Approach is now shown
  as `Phlegethos 6`, with stable checkpoint IDs.
- Focused map, reachability, hazard-spacing, shared-checkpoint, NPC dialogue,
  runtime entity, rendering, and transition tests pass. All 111 repository
  suites pass in isolated processes, and source/tools/tests compile cleanly.

- City Night 6's `Enter the sewer?` walk trigger is now one tile at the
  manhole lip instead of a broad approach zone, and City Sewer 4's
  `Climb up ladder?` trigger is likewise confined to the exact tile at the
  ladder's foot. Nearby arrivals and approach floor no longer interrupt the
  player before the feature is reached.
- City Night 5's unauthored northern highway and pavement opening now ends in
  a three-tile-deep strip of shared Astral fall terrain. The real east/west
  connections are unchanged, while the north edge no longer suggests a route
  to a nonexistent map.
- Focused Night 5, Night 6, Sewer 4, and Day 1 checks pass; all three affected
  checkpoints load and draw cleanly headlessly, and source/tools compile.

- Scratch resolution now protects Chuck from tiny pursuit enemies entering
  his footprint. A living enemy overlapping Chuck is the first target of the
  same committed swipe; otherwise the existing forward hitbox and authored
  target order are unchanged. This fixes rats and Feywild thorn mites pinning
  Chuck where his visible forward scratch could not reach them, without
  changing the scratch animation, range, controls, or one-target rule.
- Focused combat, Feywild thorn-mite, Twilight Crossroads, and modern-sewer
  checks pass; source compilation is clean and the headless game reaches and
  renders the title screen.

- The day city is built out of buildings now too, and every carriageway in the
  region -- night and day -- has a painted centre line.
- The day maps were laid out by filling everything that is not street with one
  solid char and cutting a three-row front into it where a building was wanted,
  so most of each map was a single flat colour. A new shared pass walks whatever
  building mass a map leaves behind and gives it the night treatment: parapets,
  a stepped roofline, fronts with windows, side walls turning away. It works a
  column at a time rather than on rectangles, so it dresses ragged and L-shaped
  masses without being told their shape, and it only ever writes solid chars, so
  nothing about where Chuck can walk changes.
- Road markings are measured, not authored. A road records no direction, so the
  pass measures the run of carriageway through each tile -- longer along the way
  the traffic goes -- and lays the line on the middle of it. Junctions, where
  the run is long both ways, are left unpainted. Crosswalks count as
  carriageway when measuring, or a crossing shortens the run and scatters the
  dashes across three different rows.
- The markings are their own terrain chars, so everything that asks "is this
  tile road?" had to learn them: the traffic lanes, and every respawn and
  landing check that was making sure Chuck does not come back in a live lane.

- The night city is built out of buildings now rather than blocks. A block used
  to be one mass: an unbroken field of roof with a strip of windows along its
  bottom edge, which at map scale read as a slab of plain stone taking up half
  the screen. Each block is now a terrace of several buildings sharing the
  footprint, each with its own parapet, roofline, front and side wall.
- The roof tile is tar and gravel with membrane seams and grit instead of a
  flat fill, and roofs carry plant -- air handlers and skylights -- scattered on
  a coarse lattice so nothing clumps or leaves half a roof bare.
- Parapets come in three tiles, not one. A cap laid down a vertical edge reads
  as rungs, so the left and right edges have their own tiles lit on the face
  that actually turns outward.
- The side facade stays blank. Windows were tried there and cut: staggered down
  a receding wall they read as a wavy column of dots rather than as glass, and
  they fought the front face beside them. The shading and the vertical pier
  sell the turn on their own.
- None of this changed where Chuck can walk: the footprints are solid before
  and after, tile for tile, so every route and reachability check on top of
  these blocks still measures the same thing.
- The day sheet carries the same new rows, washed for daylight, because it is
  generated from the night draws and the two sheets have to stay in step. No
  day map places the new chars yet -- that pass has not started.

- The sewer theme plays louder. It already sat in the same measured RMS window
  as the street cues, but almost all of it lives below 300Hz, and low material
  measures loud while playing quiet. Two changes: the mix leans on the pipes,
  blocks and hats that carry perceived loudness instead of piling everything
  onto the bass, and cues can now carry an authored trim applied on top of the
  stream volume, which is what actually closes the gap.
- The day-city theme is a jazz trio now rather than a slowed, held arrangement.
  The melody is still derived from the night hook in code -- that is the
  region's identity -- but underneath it there is a walking bass four to the
  bar, a ride on swung eighths, brushes on two and four, and an electric piano
  comping in syncopated stabs. The harmony moves through sixteen bars of ii-V
  motion instead of sitting on four roots, and a tenor answers the hook where
  the arrangement used to just hold. Tempo is up from 76 to 88.
- The sewer entrance is an open manhole in the sidewalk with its cover levered
  off beside it and SEWER cast into the face. It was a human-sized concrete
  opening cut into an office foundation, which read as the mouth of a subway. A
  sewer is reached through the street, so it moved out of the wall and onto the
  pavement, and the sprite canvas is sized so the *hole* -- not the sprite --
  sits over the tile that is actually solid.
- Eight test files have no `__main__` runner and were being silently skipped by
  the module-based test loop. They are run by importing and calling their
  `test_*` functions instead; all 110 suites genuinely pass.

- The Douglas fir portal is wired. Choosing YES at the forest block plays a
  short side-view cutscene: black, a night stand fading up, Chuck walking out
  of the trunk of the largest fir as if the tree were a doorway, a hold, then
  black again.
- The reveal is ordered so the environment lands first -- nothing moves until
  the fade has finished, because Chuck walking during it would steal the one
  moment the new region gets.
- The boundary is the interesting part. Phase 11 itself authored no playable
  forest content; Phase 12 now consumes the
  `doug_fir_transition_completed` flag and hands the cutscene directly into
  the playable Cabin exterior. The City Day 6 Ashtray remains the valid
  save until Chuck activates the new exterior Ashtray.

- City Day 6 is now in motion. Two businesspeople run for their lives with a
  raptor harrying each, and one police officer spins on the spot firing wide.
- Fleeing is a variant of the ordinary pedestrian patrol rather than a new
  behaviour: the same walk at sprint speed along a segment the map generator
  proved safe. That is deliberate. A pursuit AI could route somebody into the
  Astral Sea; an authored segment cannot, however hard the panic.
- Only raptors authored as chasers look at anybody but Chuck. Left emergent,
  the jungle animals drifted out of the jungle to join the chase and the
  tableau came apart, so the pairing is authored: two on the ring road after
  the two runners, three still in the undergrowth and still after Chuck. The
  chase is Chuck's cover, not a truce.
- A chaser harries rather than tackles: it closes to a standoff and holds. At
  full speed it ended up standing on the person, hiding them completely.
- The spinning officer is the Beholder fight's whirling archer standing in a
  street: the body rotates about its own centre and the aim advances a fixed
  step between rounds, so the spray sweeps rather than tracks. The lane
  officers are readable because of the aim tell; this one has no lane to read,
  so his rounds fall short instead and he is a disc to walk around. The map
  validator holds the safe route outside it.

- Added the 80x60 `City Day 6`, the phase's culminating map. Three worlds are
  visible at once: the daytime street, a patch of Chult grown up through the
  plaza, and -- inside the damaged northern building -- a block of Douglas
  fir forest at night, which is the phase's one planar portal.
- The Chult patch uses Chult's own tile draws, imported unwashed into the
  day-city sheet, so it reads as another world showing through rather than
  as city scenery. The forest block is authored against the Astral damage it
  stands beside: a cold night sky with black conifers, because the Sea is
  already a purple starfield on this map and the two must not blur.
- The tableau is one animal over one person: the massive dinosaur stands at
  the feet of a prone businessperson, with three raptors in the undergrowth.
  The prone sprite is laid across the frame rather than up it -- from this
  camera a vertical body reads as somebody standing -- and is deliberately
  restrained, a suit and a dropped umbrella with no gore. His only line is
  an ellipsis.
- The phase document forbids the chaos from making the Ashtray or the
  arrival unsafe, so the validator floods the map excluding every police
  lane and the dinosaur's whole notice radius, and proves a clear route
  still runs from the arrival to the portal.
- This is the most damaged city map: more void than every street-block map.
  City Day 5 is deliberately excluded from that comparison -- an overpass is
  three quarters sky because it is a bridge, not because the city there is
  more broken.
- The map switches to the Beholder fight theme, which is the phase's one
  deliberate music change away from a regional cue.

## Latest implementation

- Added the 46x68 `City Day 5`. A raised deck is all that survives: nine
  tiles wide with the Astral Sea on both sides, top to bottom, and traffic
  still running on it because the lights have not been told. Five of the six
  daytime maps now exist, and the density ratchet holds across all of them.
- Two spans have dropped clean out of the deck. Unlike City Day 4's square
  these jumps are the route rather than a reward -- the test asserts the exit
  is reachable by jumping and *not* reachable by walking -- which is the
  point at which the committed jump becomes load-bearing in the city.
- Because they are mandatory, fairness is what the tests prove: each gap is a
  single row with deck directly either side, and a footway crosses every gap
  so a player is never forced to launch from or land in a live traffic lane.
  The Ashtray sits before the first gap, so a missed jump costs the crossing
  rather than the map.
- The first version of that lane check was unsatisfiable -- it asked that no
  landing be road, on a deck whose middle is carriageway by construction. The
  rule that actually matters is that a pavement route exists across each gap,
  and that is what is now asserted.

## Latest implementation

- Added the 70x52 `City Day 4`. The first three daytime maps lost buildings;
  this one loses the ground. Almost 40% of it is void, and what survives is a
  street in, a ridge of pavement running round, and a civic square floating
  between them, broken into slabs with single-tile cracks showing the Astral
  Sea between.
- Crossing the square uses the committed jump the Moonmoth Fen and the sewer
  taught -- now on concrete in daylight, ramping toward City Day 6's heavier
  jump hazards. The square is tempting rather than mandatory: every cigarette
  is out on the slabs, and the tests prove both halves, that each cache needs
  a jump and that somebody who refuses to jump can still cross the map, save,
  and leave.
- The "increasingly common Astral blocks" rule is now enforced as a density
  ratchet across the whole daytime run: no map may be a smaller share of void
  than the one before it. Density rather than raw count, because a larger map
  at the same proportion is not a more damaged one. The test walks all four
  daytime maps in order and asserts the sequence never decreases.
- This map has no side facades at all, and its validator says so explicitly
  rather than inheriting the earlier maps' material checklist: there are no
  side streets left here to face onto.

## Latest implementation

- Added the 58x64 `City Day 3`. The daytime geometry keeps changing: an
  avenue, then a crossroads, and now a single street running south between
  tall faces with two alleys off it and a loading yard at the bottom. It is
  narrower than either map before it, and taller.
- The damage has stopped taking frontages and started taking buildings. The
  whole east side of the block is gone, so the pavement runs along the open
  Astral Sea for the map's full height with only a rail of collapsed kerb
  between. The test asserts the entire east column is Astral and that this
  map carries more of it than City Day 2 -- the progression is enforced from
  map to map rather than merely intended.
- Both officer types work this street: two Animal Control on the pavements
  and two police holding corners. The phase document requires both to stay
  avoidable, so the validator floods the map while excluding every net's
  notice radius *and* every police lane out to the first wall, and proves a
  clear route runs from the arrival to the way onward. It also proves no
  lane fires along the Ashtray or either doorway, and the runtime test
  checks a respawn never lands on the road or inside a net's reach.

## Latest implementation

- Composed `city_day.wav`, an original 26-bar loop in D minor at 76 BPM,
  eighty-two seconds long. The phase document allows the daytime theme to
  share a motif with the night one, so this takes that literally: the melody
  is *derived from* `city_night._HOOK` in code -- the same pitches in the
  same order, every duration stretched, the phrase spread across twice the
  bars. A test asserts the pitch sequence matches exactly, so the two can
  never drift into merely resembling each other.
- Everything around the melody changed instead. The electronic kit is gone
  entirely -- one soft brush every other bar is the only pulse -- the
  electric piano holds instead of comping, a pad sits underneath throughout,
  and the rain is mixed louder than at night because in daylight you can see
  it falling. Tests check each of those against the night arrangement rather
  than in isolation.
- The unease the document asks for is one note: a major seventh over the
  minor tonic that never resolves, so the daylight stays wrong.
- The city now runs on three cues across twelve maps, changing exactly twice
  -- at the sewer entrance and at the ladder. A test asserts each region is
  internally unbroken, that the three cues are distinct, and that all three
  files exist.

## Latest implementation

- Composed `city_sewer.wav`, an original 28-bar loop in G minor at 104 BPM,
  sixty-five seconds long. The phase document points at the memorable groove
  of classic underground music as a broad reference, so what was taken is the
  idea -- a short low-register motif under a long walk -- and nothing else.
  The riff is straight-feel sixteenth funk rising to a blue flat five and
  falling back, where the reference is a swung chromatic descent.
- The tests enforce that distance rather than trusting it: every onset lands
  on a quarter of a beat (no triplet feel), the contour must rise and return,
  and consecutive descending semitones are capped at one.
- There is no lead melody at all. The sewer maps are long and winding and a
  tune would wear out before they did, so the arrangement is bass, kit,
  clipped wood, struck pipes answering from further down the tunnel, and
  water. A test asserts every bass note sits below the night theme's melody.
- Added two instrument voices: a hollow pipe built from odd harmonics only,
  which is what makes it read as a tube rather than a bell, and a falling
  drip. Both live in the shared palette.
- Wired across all four sewer maps. The cue changes at the region boundary
  and nowhere else, and a test asserts the medieval Waterdeep sewer keeps its
  own quite different theme.

## Latest implementation

- Composed `city_night.wav`, an original 32-bar loop in D minor at 96 BPM,
  eighty seconds long. The harmony is jazz rather than pop -- ii-V motion, a
  flat-six detour, sevenths and ninths stacked four notes deep -- and the
  hook is deliberately short enough to whistle after one map, because it is
  heard across six.
- Its shape is state, harmonise, rest, return: the melody drops out entirely
  for a six-bar underpass so that its return an octave up lands. Tests assert
  that structure from the note data rather than trusting the arrangement.
- Added three instrument voices for the region: a tine electric piano for the
  jazz harmony, a clipped syncopated square bass, and a filtered noise wash
  that keeps wet air under everything. They live in the shared instrument
  palette, not in the composition.
- The render clears the same gates the earlier area themes are held to:
  eighty seconds, peak 0.72, RMS level with Chult and the Feywild, and a loop
  seam far tighter than the temple's. The first render sat noticeably quieter
  than its neighbours and the headroom was lifted to match.
- Wired across all six night maps so the cue never restarts between them, per
  the phase document's continuity rule. The sewer and day city stay silent
  until their own themes are composed, and a test asserts they never borrow
  this one.

## Latest implementation

- Added police officers as stationary ranged hazards. The phase document asks
  to reuse the spined devil's projectile architecture where practical, so a
  bullet is literally that projectile subclassed: the same travel, the same
  "stops dead against solid geometry" rule, retuned faster and smaller. The
  devil's spine gained a `speed` class attribute so this reuse needed no
  copying, and its behaviour is unchanged.
- What the devil lacks and an officer has is a tell. The weapon comes up for
  most of a second before each shot, with a muzzle flash on the shot itself,
  so a lane can always be read before it is live. That is the difference
  between a hazard to route around and an ambush, and a test asserts the aim
  immediately precedes the round rather than merely occurring sometimes.
- Officers never move and reset with the map. Two hold posts on City Day 2,
  and a test walks each lane tile by tile to prove it reaches neither the
  Ashtray nor the arrival before hitting a wall -- a hazard to route around
  must never fire on a respawn point.
- Chuck gains nothing ranged of his own; a test asserts the player has no
  firing method and that officers cannot be scratched.

## Latest implementation

- Added Animal Control officers as a subclass of the undead pursuer rather
  than a new entity. Durability, contact damage and the straightforward walk
  are inherited whole and match a Chult zombie exactly; the only new thing is
  the net.
- The net winds up visibly before it is thrown, so being caught is always
  something Chuck had a moment to see coming, and the throw is a one-frame
  event the scene consumes rather than a state that re-arms itself.
- Being caught is deliberately not a second way to die. It is a scene state
  alongside the climb, the fall and the respawn: Chuck is held still, Sanity
  drains continuously to zero over four seconds, and then the *existing*
  depletion hook runs -- the same quiet disappearance and Astral Anchor
  return as anything else. A test asserts exactly one depletion fires.
- The drain is computed from total elapsed time rather than subtracted frame
  by frame, so a quarter-second frame and a 240Hz frame leave Sanity in the
  same place. The tests check that at four different step sizes.
- Map reset and leaving the map both clear any active net, and a net overlay
  draws over Chuck so the held state is readable.
- Two officers stand on City Day 2's wide pavements with a road between them
  and the route. Tests assert neither the Ashtray nor the arrival is inside
  an officer's notice range, and that neither stands in a traffic lane.
- Fixed City Day 2's west arrival, which sat in a live traffic lane.

## Latest implementation

- Added the 76x58 `City Day 2`. City Day 1 was one broad avenue with a plaza;
  this is the other thing a city is -- a junction, two streets meeting at
  right angles with traffic running on both, so a crossing has to be timed
  twice rather than once. The traffic-lane markers are the night region's,
  reused unchanged.
- The daytime damage is spreading, as the phase document asks: the whole
  north-west quarter of the junction is simply gone, and the streets that
  served it end in it rather than at an invisible wall. The test compares
  this map's Astral count against City Day 1's rather than just counting it,
  so the progression is enforced and not merely intended.
- The map carries its own Ashtray on a safe pavement, four cigarettes, three
  businesspeople, and reciprocal travel with City Day 1. The woman in the red
  dress deliberately stays on City Day 1, where her long patrol makes her
  that street's landmark. No homeless man in the daytime region.

## Latest implementation

- Added the `city_day` tileset. The daytime city is the same city, so its
  generator imports the night sheet's own draw functions and washes flat
  overcast daylight over the result rather than authoring a second set of
  buildings that could drift out of step. Only two rows are authored
  separately: windows, which stop glowing because nobody leaves a lamp on at
  noon, and standing puddles, because rain reads on the ground in daylight
  and vanished into the dark at night. A test asserts the day sheet is
  measurably brighter than the night sheet row for row.
- Added the 88x44 `City Day 1`, reached by the ladder. Its geometry is
  deliberately looser than the night blocks -- one broad avenue, a plaza off
  it, and a side street north -- and daylight shows the damage: the avenue
  runs west and simply stops in Astral blocks rather than an invisible wall.
- Wired City Sewer 4's `Climb up ladder?` prompt, which fires from the floor
  at the ladder's foot so Chuck is on ordinary ground when asked. NO closes
  silently. The reservation test that guarded this is now replaced by one
  that exercises the real climb.
- Added the woman in the red dress. She is the businessperson's exact
  silhouette and umbrella in the one colour nothing else in this city wears,
  and she says what everyone says. Pedestrian patrol range became per-NPC so
  hers can be four times the default: that length, plus the dress, is the
  whole of what makes her a landmark rather than another commuter.
- It is still raining in the daytime city; only the sewer below is dry.

## Latest implementation

- Added the 54x50 `City Sewer 4`. All four sewer maps are now playable and
  connected, and the region turns four times rather than running in
  parallel: east, then south, then back west, and now north and climbing.
  The test asserts the route climbs more than it runs, which is the property
  that matters -- not the shape of the bounding box.
- Added a modern maintenance ladder as two cells forming one human-scale
  16x32 structure, the same shape as the ship's ladder. It is set against
  the chamber's north wall so it climbs into the ceiling, and its head shows
  grey daylight -- the only light down here that is not a utility lamp, so
  the way out reads before it is reached.
- The ladder is deliberately still scenery. Its `Climb up ladder?` prompt
  belongs to the pass that authors City Day 1, exactly as the sewer
  entrance's prompt waited for City Sewer 1: a visible way on is honest, a
  prompt that leads nowhere is not. A test holds that reservation so it
  cannot be quietly forgotten.
- The map carries its own Ashtray, four pursuing rats, three cigarettes, and
  two sludge pools, and reciprocal travel to City Sewer 3 both ways.

## Latest implementation

- Added the 84x40 `City Sewer 3`. The region now turns three ways: Sewer 1
  ran east, Sewer 2 dropped south, and this one doubles back west, so the
  four sewer maps never become parallel corridors.
- Added the crocodile as a fourth kind in the existing undead role rather
  than a new entity: as durable and as dangerous on contact as a Chult
  zombie, but half again as fast, with the same straightforward pursuit. Its
  16x30 sheet is the undead frame read top-down, where a long narrow animal
  fits better than an upright person does; the turning frame is drawn curved
  so its mass matches the head-on frames instead of halving.
- The hall's middle is a sludge channel the crocodile lives in, crossed by a
  north maintenance walkway and a south ledge with two connectors between
  them. The phase document requires the animal stay avoidable, so a
  notice-aware flood proves a route to the far side exists that never enters
  its notice range -- while the channel itself stays contested.
- Sludge is what makes it dangerous: slowed to 0.42 speed Chuck is still
  quicker than it, but not by much, and the test asserts that margin rather
  than assuming it.
- Sewer 2's reserved southern end is now a marked hole in the collapsed
  floor dropping into Sewer 3, wired both ways, with the return arrival set
  down beside the hole rather than in it.

## Latest implementation

- Added toxic green sludge as the sewer's single new terrain hazard. It is
  not new code: it registers in the same table that gives Chult thorns their
  Sanity damage and the same table that gives Feywild pollen its slowdown.
  Generalising the second of those from one pollen constant to a small
  terrain-to-multiplier map was the only engine change, and the slowest
  terrain under the footprint now wins. Sludge bites harder than thorns and
  drags harder than pollen, so it reads as something to cross deliberately.
- Sludge is deliberately its own colour: bright toxic green with surfacing
  bubbles, unmistakable against the dark channel and the grey wet floor.
- Rebuilt City Sewer 2's lower shaft as the phase's harder jump course: nine
  single-tile Astral gaps between narrow concrete ledges, turning twice
  rather than dropping straight. The shaft either side of the course is
  solid, so the course is the only way down. Validation proves the chamber
  below is reachable with the committed jump, unreachable by walking, that
  every gap is one tile across its crossed axis, and that no two gaps meet
  at a corner -- which would silently create an unjumpable two-tile crossing.
- Sludge pressures the approaches and the landing chamber but never a ledge
  or a jump's launch or landing tile; a slowed launch off a one-tile ledge
  would not be fair. The map's one Ashtray moved onto the jog above the drop,
  outside the course and clear of every rat.

## Latest implementation

- Added the 46x62 `City Sewer 2`: three shafts stepping down and back west,
  joined by two jogs, so the route turns four times and never runs straight.
  It is deliberately the opposite shape to Sewer 1, which is wider than it is
  tall, and the tests assert that contrast directly.
- Opened Sewer 1's reserved continuation as a side culvert off its east leg,
  wired both ways. Its southern Astral damage stays exactly as authored --
  that ruin is scenery now rather than a placeholder, so the route turns
  instead of pushing through it.
- Added the map's physical Ashtray/shared-loader `City Sewer 2` checkpoint,
  three cigarettes, and six spaced rats using the same aggressive ship-hold
  pursuit. Pursuit respects shaft walls, no rat waits on the Ashtray Chuck
  respawns at, and Sanity-zero return restores all six.
- Wall decoration only ever redecorates a tile that is already wall, so a
  brick or pipe run can never accidentally close a shaft; it is laid as a
  continuous band rather than scattered, which is what gives Sewer 1 its
  crisp tunnel edges.
- The southern end stays visibly collided, reserved for Sewer 3. No toxic
  sludge and no Astral jump sequence in this slice.

## Latest implementation

- Added the 92x38 `City Sewer 1` map as a long three-leg route: north from the
  city stairs, east beside a drainage channel, then south toward an
  Astral-severed future continuation. Its narrow camera framing and route turns
  establish the intended urban-sewer movement rhythm without adding City
  Sewer 2, toxic sludge, or the later jump challenge.
- Added a dedicated procedural `city_sewer` tileset with poured concrete,
  gray brick repairs, exposed metal pipes, animated utility lamps, slab and
  maintenance floors, safe wet patches, warning stripes, animated runoff,
  and exact shared Astral fall tiles. It is visually and technically distinct
  from Waterdeep's medieval dirt-and-mud sewer.
- Wired City Night 6's existing `Enter the sewer?` YES branch to the authored
  `from_city_night_6` arrival; NO still closes with no further text. Added a
  validated optional facing field to the reusable data-driven choice path so
  Chuck enters facing into the tunnel. The southern sewer threshold returns
  normally to an aligned arrival outside the city entrance.
- Added the map's physical Ashtray/shared-loader `City Sewer 1` checkpoint,
  three loose cigarettes, and five spaced rats using the exact aggressive
  ship-hold notice/pursuit behavior. Pursuit respects solid and Astral fall
  collision, and Sanity-zero return restores every rat at the local Ashtray.
- Focused coverage validates topology, material language, entrance/return
  transitions, checkpoint loading, choice facing, rat pursuit/collision/reset,
  native rendering, and removal of exterior rain inside the tunnel. All 95
  test suites pass in isolated processes; compilation and headless title/City
  Sewer 1 launches are clean.

- Added the connected 88x60 `City Night 6` map and opened City Night 5's
  western approach as its aligned reciprocal route. Four intact 32x20 office
  masses frame an east/west street and north/south crossing; every unauthored
  exterior edge remains visibly severed by exact shared Astral fall terrain.
- Added the map's physical Ashtray/shared-loader `City Night 6` checkpoint,
  four loose cigarettes, persistent rain, one avoidable raccoon, two
  stationary businesspeople, one vertical-patrol businessperson, and two
  deterministic traffic lanes. Normal Sanity return resets both traffic and
  the raccoon.
- Added an 80x64 procedural open concrete sewer entrance embedded in the
  northwest office facade. Its black worker-scale arch, descending steps,
  rails, and shallow walk trigger clearly distinguish it from the Waterdeep
  grate and display the exact `Enter the sewer?` YES/NO prompt on approach.
- Both options close silently for this bounded threshold pass. The YES branch
  remains deliberately data-local and gains its `City Sewer 1` destination
  when that next map is authored, avoiding either a broken goto or a premature
  placeholder sewer map.
- Focused coverage validates topology, office scale, safe reachability,
  Map 5/6 alignment, entrance scale/art/prompt, shared checkpoint loading,
  native rendering, and death reset. All 94 test suites pass in isolated
  processes; compilation and headless title/City Night 6 launches are clean.

- Added the connected 112x48 `City Night 5` highway map and opened City Night
  4's western sidewalk as its aligned reciprocal route. Four full-size office
  masses frame an east/west pedestrian corridor; the still-unauthored western
  route remains visibly severed by exact shared Astral fall terrain.
- Built two sixteen-tile carriageways with eight alternating north/south
  traffic lanes, broad zebra markings, safe approach sidewalks, and a
  ten-tile central median. Deterministic spacing creates staged readable
  pauses without adding a second traffic implementation or accumulating cars.
- Added the map's physical Ashtray and shared-loader `City Night 5`
  checkpoint, five loose cigarettes, persistent rain, one avoidable raccoon,
  two stationary businesspeople, and one median patrol businessperson. Sanity
  return resets both the raccoon and all eight lanes to their authored state.
- Added focused topology, office-scale, median/crosswalk, entrance-alignment,
  checkpoint, entity, traffic-population, native-render, and respawn coverage.
  All 93 test suites pass in isolated processes; compilation and headless
  title/City Night 5 launch checks are clean.

- Added the connected 84x60 `City Night 4` map and opened City Night 3's
  northern sidewalk as its reciprocal route. Unequal setbacks distinguish the
  new intersection while retaining four indivisible office masses at credible
  city-block scale; every unused edge remains visibly severed by Astral Sea.
- Added the map's physical Ashtray and shared-loader `City Night 4`
  checkpoint, four loose cigarettes, persistent rain, two avoidable raccoons,
  two stationary businesspeople, one horizontal-patrol businessperson, and a
  two-lane east/west crossing. The one homeless man remains only in Map 3.
- Added focused coverage for topology, large-building bounds, discovery
  reachability, exact Map 3/4 entrance alignment, checkpoint registration,
  scene composition, traffic direction, native rendering, and Sanity-zero
  Ashtray return with raccoon reset. City Night 5 remains outside this slice.
- All 92 test suites pass in isolated processes, compilation is clean, and
  the title loop plus City Night 4 checkpoint launch headlessly. The native
  arrival composition was visually inspected.

- Added the connected 80x56 `City Night 3` map and opened City Night 2's
  eastern sidewalk as its reciprocal route. Four full city-block office
  masses frame a wider cross street; all other apparent continuations remain
  physically severed by shared Astral fall tiles until their maps exist.
- Added the map's physical Ashtray and shared-loader `City Night 3`
  checkpoint, four loose cigarettes, persistent rain, two avoidable raccoons,
  one stationary businessperson, and one vertical-patrol businessperson.
  North/south traffic lanes change the crossing rhythm from the earlier
  east/west cars without approaching highway-map density.
- Added the one approved homeless man as a seated, non-patrolling NPC beside
  two clusters of oversized bottles. His only line is the exact approved
  `Hey there buddy!`; businesspeople retain `Ah! A rat!`. New sprites remain
  within the established human NPC scale and procedural pixel-art language.
- Added focused coverage for map scale/topology, safe discovery routes,
  visual/actual entrance alignment, exact NPC counts and dialogue, checkpoint
  registration, vertical traffic, props, rain, rendering, and regional
  regressions. City Night 4 and the highway remain outside this slice.
- All 91 test suites pass in isolated processes, compilation is clean, and
  the title loop plus City Night 3 checkpoint launch headlessly. The native
  arrival/homeless-scene composition was visually inspected.

- Added the connected 76x56 `City Night 2` map. Four indivisible office
  blocks (each at least 28x18 tiles) frame a broad street/sidewalk grid, and
  every unauthored route still ends visibly in shared Astral fall terrain.
  The reciprocal southern street opening lines up with City Night 1's newly
  authored northern continuation.
- Added this map's physical Ashtray and shared-loader `City Night 2`
  development checkpoint, four loose cigarettes, continuous rain, and a
  second two-lane crossing. The checkpoint uses the normal save, Continue,
  Sanity-zero return, and enemy-reset paths.
- Introduced two stationary businesspeople plus one short-patrol pedestrian,
  all using the exact dialogue `Ah! A rat!`. Introduced one avoidable raccoon
  with direct pursuit, 15 Sanity contact damage, and three-scratch durability:
  stronger than rats, substantially weaker than Chult zombies.
- Extracted the large-office painter for reuse by later city generators and
  added focused topology, transition, checkpoint, dialogue, rain, pedestrian,
  combat, and reset coverage. The homeless NPC, highway, City Night 3, and
  dedicated night-city soundtrack remain outside this slice.
- All 90 test suites pass in isolated processes, compilation is clean, and
  both the title loop and City Night 2 checkpoint render launch headlessly.
  The native checkpoint view was visually inspected.

- Added Phase 11's reusable deterministic traffic system and City Night 1's
  first teaching crossing. Two opposed lanes carry fixed populations of
  fast, human-scale cars across a worn zebra crossing; broad deterministic
  gaps let the player observe a safe window before committing.
- Traffic is a non-combat environmental hazard. Each impact costs 50 Sanity,
  plays the established hurt feedback, and returns Chuck to his last safe
  non-road footing so a vehicle cannot embed him or push him out of bounds.
  A lethal second impact uses the normal active-Ashtray death/return and resets
  every lane to its authored phase.
- The reusable lane controller supports all four directions, wraps cars at
  credible map boundaries, and owns a fixed vehicle count so extended play
  cannot accumulate entities. Four procedural top-down car variants establish
  the modern human scale.
- All 89 isolated test suites pass, compilation is clean, and the active rainy
  crossing was visually inspected from its playable approach.

- Reworked City Night 1 around a true city grid and increased it from 56x36
  to 72x54 tiles. Four large, indivisible office blocks now flank the road and
  sidewalk cross; each solid building mass is at least 21x18 tiles, and broad
  setbacks provide the optional sidewalk pockets without leaving narrow
  freestanding office strips.
- Replaced the flat repeated wall treatment with a reusable three-quarter-view
  office language: broad inaccessible roof planes, cornices, eight-tile-deep
  facades, darker side columns, and restrained three-frame rain/window glints.
  The Phase 11 contract and topology tests now prohibit thin office masses in
  future city maps.
- Preserved all four cigarette pickups, the rainy presentation, exact Astral
  edge hazards, and the authoritative City Night 1 checkpoint/save IDs; the
  physical Ashtray coordinates now match the larger grid.
- All 88 isolated test suites pass, compilation is clean, and both full-map
  and playable-checkpoint renders were visually inspected.

- Corrected the Zephyros introduction window layering. Its drifting exterior
  cloud is now clipped to the blue opening, so the dark reveal and tower
  masonry remain in front and the cloud can no longer appear inside the room.
  Focused visual/pixel regression coverage and compilation are clean.

- Began Phase 11 with a bounded City Night 1 foundation pass. The former
  24x16 endpoint became a rainy city map built around a broad cross
  street, four human-scale building masses, wet sidewalk lanes, two optional
  pockets, window bands, and four scattered single-cigarette pickups.
- Every currently unauthored street or sidewalk continuation ends visibly in
  exact shared animated Astral fall-hazard terrain. No decorative blocker or
  separate portal behavior was introduced.
- Preserved the authoritative `modern_city_arrival`, `modern_city_1`, and
  `modern_city_anchor` IDs so existing cutscene and save data remain valid.
  Their display names now read `City Night 1` / `City Night 1 Ashtray`, and
  the Ashtray checkpoint position matches the expanded map.
- Added deterministic map generation plus focused tests for safe discovery
  reachability, map scale/materials, exact Astral-art reuse, checkpoint
  compatibility, and the unchanged Phase 10 handoff. Traffic, city NPCs,
  raccoons, City Night 2, and the night-city soundtrack remain deliberately
  outside this slice.
- All 88 test files pass in isolated processes. Compilation and headless title
  plus City Night 1 frame launches are clean.

- Authored `docs/development/PHASE-11.md` from the approved rainy-city notes.
  The next phase is scoped to sixteen playable maps: six rainy night-city
  maps, four modern urban-sewer maps, and six rainy day-city maps, ending at
  the short Doug Fir Forest at Night handoff. This documentation-only pass
  adds no Phase 11 gameplay yet.
- The contract formalizes traffic/Frogger traversal, city NPC dialogue,
  raccoons, aggressive sewer rats, one crocodile, combined toxic-sludge
  slowing/damage, Animal Control net capture, police projectiles, the final
  Chult/Astral collision tableau, regional audio, one Ashtray per map, and
  shared-loader development checkpoints.
- Added a denser freestanding-mushroom pass across the later Feywild. Giant
  Tea Table through Twilight Crossroads now receive six additional, widely
  spaced mushrooms per map, and the peaceful Cloud Staircase approach receives
  six as well. Maps 1--4 retain their existing 3--4 mushrooms, making the
  region's visual progression intentionally fuller from Map 5 onward.
- Mushroom coordinates are shared by procedural generators and authored map
  files. Placements occupy broad pockets or already-solid hedge growth; all
  87 standalone suites pass, including every affected Map 5--13
  traversal/encounter suite and the Cloud Staircase suite.
- Fixed committed-jump landing validation across solid-but-jumpable water.
  Chuck may still clear a one-tile channel and land normally on dry ground,
  Feywild stepping stones, or raised lily pads, but a hop that ends over water
  now returns him to the last safe point instead of leaving him walking inside
  the water collision.
- Added focused regression coverage for rejected water landings and successful
  stone/pad landings. The Moonmoth Fen, Luminous Rapids, and Phlegethos river
  suites remain clean.
- Corrected the Giant Tea Table furniture cleanup: restored the four structural
  table legs beneath the tabletop and removed the three unexplained
  freestanding chair-leg props east of it. Western chair legs, the under-table
  route, apron, shadow, and tabletop place settings remain intact.
- Exact-coordinate coverage now protects both sets of furniture. All 86
  standalone suites pass; compilation and the title-frame launch are clean.
- Realigned all 26 reciprocal arrivals across the 13 connected Feywild map
  boundaries. Chuck now appears on the centerline exactly one safe tile inside
  the visible wilderness opening instead of several tiles away; the Pollen
  Orchard's formerly off-center southern arrival is also corrected.
- Added a region-wide regression test deriving each destination entrance from
  the shared transition registry, so future Feywild arrivals must remain
  centered and adjacent to their actual visual threshold.
- All 86 standalone suites pass; compilation and the headless title-frame
  launch check are clean.
- Completed Phase 10's three-cue audio pass with
  `zephyros_launch_city.wav`, an original 48-second D-minor one-shot at 120
  BPM. It preserves the established falling motif while progressively adding
  Astral pulse, wind swells, rain-like percussion, struck-city metal, and a
  restrained low synth as modern fragments overtake the sky.
- The cue continues unchanged across the launch-to-rainy-city scene handoff.
  Its action layers stop at sidewalk impact, leaving rain, distant metal,
  bells, and tired flute beneath Chuck's death, return, look-around, and
  cigarette drag; it fades with the final visual fade into the contained city
  checkpoint rather than cutting abruptly.
- All three specified Phase 10 cues and their transitions are complete. The
  next development boundary is Phase 11's modern-city gameplay, which should
  not begin until its authoritative phase document is available.
- Added the second Phase 10 soundtrack: `zephyros_conversation.wav`, an
  original 111-second G-major/Mixolydian loop at 78 BPM. A warm reed carries a
  recurring patient melody over soft mallets, round bass, gentle plucks,
  cloud pads, sparse bells, reverse swells, and small wooden ticks.
- The existing tower cue now fades for 900 ms while Zephyros' hand settles;
  the warmer conversation theme begins with the first manually advanced
  dialogue panel. The transition is guarded against accidental hard cuts on
  unusually long frames. The launch/modern-city arrangement is the next and
  final Phase 10 audio slice.
- Added the first Phase 10 soundtrack: `zephyros_tower.wav`, an original
  105-second C-Lydian loop at 82 BPM. A patient recurring flute melody floats
  over glassy mallets, open-fifth bass, sparse high bells, reverse swells, and
  a new slow-blooming cloud-pad voice for a peaceful, ancient sense of height.
- The Cloud Staircase, tower exterior, and Aerie all request the same cue, so
  the audio system carries it continuously between maps without restarting.
  Its sustained mix is level-matched to the Feywild theme without sacrificing
  the quieter arrangement. Zephyros' conversation now has its own warmer cue.
- Polished the Zephyros/launch/city cinematic chain. Zephyros' hand now travels
  across the room to Chuck at the rope instead of Chuck sliding toward a fixed
  palm, and his purple robe continues through the bottom of the frame rather
  than ending as a floating bust.
- Consolidated the unchanged Zephyros speech from 36 tiny automatic beats into
  19 readable panels. The conversation now uses normal player-controlled
  typewriter completion and advance behavior and waits on every panel.
- Delayed the launch music until 3.5 seconds into the fling and removed the
  unexplained black perspective-road rectangle and converging lines from the
  rainy modern-city descent.
- Rescaled Zephyros' exterior approach: the suspended platform is now a
  compact stone island roughly half its previous footprint, while the tower
  facade and embedded Aerie arch have expanded from 192x128 to 320x224 pixels.
  The tower fills and extends beyond the native viewport, and its doorway alone
  dwarfs Chuck. The existing Ashtray, arrival, and Aerie transition are intact.
- The city-fragment collision now continues automatically into a long
  diagonal descent through a rain-dark modern street canyon. Chuck gradually
  loses horizontal momentum before dropping the remaining distance to a wet
  sidewalk.
- Sidewalk impact sets the cinematic Sanity state to zero, plays the
  established hurt/vanish/respawn sequence, and reforms Chuck beside the first
  city Ashtray. He quietly looks left, right, and forward, puts in a cigarette,
  and takes a drag before the scene fades back to gameplay.
- Added a contained 24x16 modern-city arrival map with procedural rain-dark
  masonry, office windows, wet sidewalk, curb, animated road glints, and
  persistent screen-space rain. It has exactly one physical Ashtray and no
  exits, NPCs, enemies, interiors, or Phase 11 gameplay.
- `City 1` is available in the development selector. The cinematic activates
  and saves `modern_city_anchor`, then loads it through the same shared
  checkpoint path used by Continue; the new `modern_city_reached` flag restores
  the endpoint reliably.
- All 85 standalone test suites pass. Compilation and the headless title-frame
  launch check are clean.
- The held final Zephyros line now continues directly into a dedicated launch
  scene. A complete distant tower remains in frame while Zephyros makes one
  small, effortless hand motion and Chuck crosses the sky as a two-pixel dot.
- The close flight begins horizontally, with Chuck entering from the west and
  holding altitude before gravity gradually pulls him downward. The existing
  `fall_to_chult.wav` motif begins once after a short fade from the Feywild
  track; Phase 10's final transition arrangement remains part of the audio
  pass.
- Exact animated Astral fall-hazard tiles enter first. Office-wall sections,
  lit windows, jagged concrete pieces, and violet collision seams then mix
  into the same moving sky until Chuck visibly strikes a large city fragment.
  That impact now holds as the stable boundary before the rainy descent.
- Rope `YES` now starts a dedicated Zephyros introduction scene
  while `NO` still closes silently. Chuck descends a giant rope against
  cloud-giant masonry, Zephyros' impossibly large face enters slowly, blinks,
  smiles, and raises a palm for Chuck to step onto.
- Zephyros uses a warm blue-grey procedural portrait with softly raised brows,
  gold earrings, purple-and-gold clothes, and a long white beard. His face
  fills the native frame while Chuck remains a tiny readable figure on the
  palm beside it.
- The complete supplied conversation is stored in dialogue data and grouped
  into 19 normally advanced panels. The final `I shall fling you onward!`
  tableau hands directly into the launch scene; the dedicated Phase 10
  conversation music is now implemented by the second audio pass.
- Added the 60x46 open-sided Aerie beyond the exterior arch. Its broad stone
  floor now follows a clearly rounded elliptical tower plan rather than a
  square-like clipped outline. Four enormous seven-tile nests ring a solid,
  near-black opening into the tower interior; the giant descending rope is
  visibly lashed to an iron cleat on the south stone lip.
- One griffon emerges from the northwest nest and reuses the established slow
  massive-hazard behavior and reset lifecycle. It begins far outside notice
  range, is much slower than Chuck, and never gates the rope or return route.
- Added the exact walk-triggered `Climb down the rope?` YES/NO prompt. `YES`
  now dispatches the introduction through the validated scene-action seam;
  `NO` closes with no additional text.
- Added the physical `Zephyros 3 Ashtray`, shared `Zephyros 3` development
  checkpoint, reversible exterior travel, procedural nest/rope/griffon art,
  and focused navigation, scale, enemy, choice, transition, and save coverage.
- Recut the tower ascent into a 19.5-second two-scale sequence. The first
  eight-plus seconds keep Chuck readable against a frame-filling giant stone
  wall; a cloud-white cut then reveals the complete tower and staircase from a
  distance where Chuck is intentionally too small to draw. The distant shot
  holds for a clear six-and-a-half-second upward stair retraction before the
  existing exterior handoff.
- Tightened the Cloud Staircase prompt from a broad five-by-three-tile zone to
  a shallow two-by-one zone directly against the stair's base. Chuck can now
  approach close enough to see the cloud plinth and ascending steps before the
  YES/NO overlay appears and the cutscene can begin.
- Reworked the tower exterior's north entrance from a freestanding arch into
  a twelve-tile-wide curved tower facade. Pale masonry now continues behind
  and around the black threshold and off the north side of the view, making it
  clear the arch enters the Aerie rather than opening onto empty sky.
- Added the peaceful 64x44 Cloud Staircase map west of Twilight Crossroads.
  Its immense stair dominates a quiet Feywild clearing with no combat, one
  physical Ashtray, and a wilderness opening back to Feywild 13.
- Approaching the stair asks `Climb the cloud staircase?`; `NO` closes
  silently and `YES` runs a dedicated, input-free side-view climb in which the
  cloud stair retracts into Zephyros' tall pale tower.
- The cutscene fades into the playable 44x34 circular tower exterior with
  animated open sky, drifting clouds, a giant north arch, and its own physical
  Ashtray. The arch connects normally to the playable Aerie.
- `Zephyros 1` and `Zephyros 2` use the same checkpoint loader as normal saves
  and preserve Sanity across the cinematic handoff. Focused coverage validates
  the route, exact choice behavior, maps, procedural art, and checkpoints.

## Next logical task

Playtest the inserted Fractured Way in normal sequence and from its development
checkpoint. Phase 11 is otherwise feature-complete; begin Phase 12 only after
its scope document exists.

## Current state

- Phase 8 now has six connected playable Phlegethos maps: Arrival, Lava Road,
  Lava Lake, Rubble Pass, Fractured Way, and Fortress Approach.
- The new 64x34 Rubble Pass sits between the Lava Lake and Fortress and turns
  the route west-to-east. A broad paved lane winds through 127 pieces of dark
  basalt-and-ember rubble, crosses a narrow two-tile lava river on an intact
  slab, and passes a 48x96 cliff-fed lava fall. One slow lemure starts beyond
  notice range at the west end; one slow horned devil remains optional beyond
  notice range from the required route. The map has its own Ashtray,
  development checkpoint `Phlegethos 4`, three breakable carton urns, and
  uninterrupted Phlegethos music. Fractured Way is displayed as
  `Phlegethos 5`, and the fortress as `Phlegethos 6`; their persisted
  checkpoint IDs are stable.
- The Rubble Pass's east exit no longer borrows a misaligned temple arch. A
  three-tile-tall infernal wall cleft is centered on the paved approach, and
  every visible dark doorway cell is the actual transition trigger. The
  cliff-fed lava fall now cycles through four procedural ribbon, highlight,
  and impact frames. In the fortress tableau, the wizard stands clear to the
  east of the enlarged Pit Fiend rather than being hidden behind its 128px
  sprite.
- The complete Phase 8 enemy set is present: lemures, fire snakes, spined
  devils, flameskulls, and horned devils, all built as variants or extensions
  of established enemy/hazard systems.
- Seventeen temple-style breakable urns are distributed across the five
  original Phlegethos maps: three each in Arrival and Lava Road, four on the Lava
  Lake's two safe shores, three in the Rubble Pass, and four around the
  Fortress yard. They reuse the
  exact temple scratch/shatter/reset lifecycle and each drops the established
  20-cigarette carton. Placements stay off required routes, stepping stones,
  checkpoints, and the fortress battle aisle.
- The fortress yard now shows the returning fighter, wizard, and ranger
  actively battling a massive 128x128 Pit Fiend, now more than four times a
  human enemy's sprite height. A Phlegethos-specific choreographer
  reuses the shared battle projectile path: the ranger aims at the fiend, the
  wizard fires bolt fans, the fighter holds lesser devils, and the fiend
  returns fire. Automatic entry dialogue establishes that the trio is trying
  to repair the spreading fractures.
- Road and Lake Ashtray marker IDs now match the checkpoint registry. Their
  previous mismatch crashed on activation; regression coverage now validates
  every authored Phase 8 Ashtray against a saveable same-map definition.
- Entering the upper fortress yard now triggers escalating Astral corruption:
  a continuous two-row band cuts off retreat, then three timed jagged waves
  advance from the arena's sides. They use the exact animated Astral fall
  tiles, never materialize under Chuck, preserve a broad central route through
  the complete climax, and restore completely on death/reset.
- Ten hard-edged Feywild river fragments begin flowing west through staggered
  arena lanes after the third Astral wave. Six seconds later, eighteen more
  blocks align into a continuous arena-height surge and sweep west, making
  river contact inevitable while Astral tiles remain easy to route around.
  Walking or jumping into any river block now starts Chuck's shared
  shrink-and-sink fall animation; after the animation completes, Sanity is
  preserved and the dedicated input-free river cutscene begins.
- The Phase 8 ending is complete. It opens fully black and slowly reveals a
  35-second river journey suspended between collided worlds. Basalt banks give
  way to dense enchanted growth, luminous spiral plants, glowing flowers,
  mushrooms, saturated violet/cyan accents, oversized roots, and vibrant
  vegetation. Chuck remains clearly visible in the current through the longer
  rush and waterfall, enters calmer water, then visibly washes out prone onto
  the bank. He lies still, slowly pushes himself upright, and stands before the
  final black fade. The scene reuses the established fall soundtrack and
  carries Sanity across the fortress handoff.
- The detached horizontal foam stroke that appeared beside Chuck as he washed
  onto the Feywild bank has been removed; the river and shoreline animation
  otherwise remain unchanged.
- By direct instruction, the final black now resolves into the first playable
  Feywild area: a 52x36 enemy-free riverbank. Chuck wakes beside the broad
  animated teal river, reaches the nearby `Feywild Ashtray`, and follows a
  winding, branching path through dense enchanted growth toward an inert
  deeper-Feywild boundary. A dedicated procedural tileset and reusable tree,
  luminous spiral-plant, and mushroom props carry the cutscene's cyan,
  emerald, violet, and pink visual language into normal top-down play.
- `Feywild 1` uses the shared checkpoint loader and development selector;
  `feywild_reached` is the only new durable progression flag. Loading directly
  or arriving from the cutscene preserves the normal checkpoint/Sanity
  architecture, and the map-local Ashtray is the sole save/respawn point.
  Phase 9 is now specified in `docs/development/PHASE-9.md` as a thirteen-map
  Feywild region: the existing riverbank plus twelve new maps built around
  reactive flower switches, slowing pollen, Chuck-sized passages, and a
  Feywild-specific enemy scale.
- `Feywild 2` (Blooming Path) is now a connected 60x42, enemy-free enchanted
  clearing with one Ashtray, two cigarette-grass tufts, dense
  oversized vegetation, and valid paths both back to the Riverbank and toward
  the inert Map 3 boundary. Its shared development checkpoint and map-local
  save checkpoint both use the existing checkpoint loader.
- The first reusable reactive-flower group is live. Chuck scratches the
  central flower with the normal attack; it pulses before three authored
  vegetation cells retract and three others close, swapping a winding upper
  route for a direct lower route. The change is reversible, waits if Chuck
  occupies a target cell, cannot strand him in either authored state, and
  resets on death, map reload, or Continue rather than expanding the save
  format. One grass tuft now grows immediately beside this first flower; a
  casual scratch aimed between them prioritizes the flower, providing a
  natural accidental demonstration while leaving the grass reward intact.
- `Feywild 3` (Pollen Orchard) is a connected 62x46 enemy-free map with five
  shallow pollen beds, winding orchard lanes, one Ashtray, an optional
  cigarette-grass pocket, and an inert Rootways boundary. Its reversible
  flower exchanges a long eastern detour for a direct middle lane while both
  configurations preserve all required routes.
- Slowing pollen is implemented as a reusable immediate terrain effect rather
  than a status system. Animated low flowers and drifting gold, pink, and cyan
  motes visibly mark the walkable terrain. Grounded contact applies one
  consistent 0.48 movement multiplier; leaving restores full speed, jumping
  remains unaffected, and pollen never damages Sanity or behaves as a fall
  hazard. `Feywild 3` and its Ashtray use the shared checkpoint loader.
- Every current Feywild transition threshold now uses Chult's actual boundary
  structure: a contiguous three-tile wilderness mouth cut through the outer
  map edge, reached by a visible trail. Cardinal enchanted leaves, vines, and
  saturated accents render overhead while all three cells use the established
  walk-transition terrain. No between-map exit remains as a single opening
  embedded inside the vegetation field.
- The Feywild now has its own 99-second regional soundtrack at 116 BPM. Its
  recurring syncopated mallet hook, elastic scooped bass, hand percussion,
  woody reed answers, restrained reverse-bell swells, and F Mixolydian harmony
  make it catchy and funky while retaining mysterious enchanted color.
  Later peaks use only isolated echo accents, reserve reed answers for
  contrasting sections, and avoid added bass/percussion fills so the hook
  remains clear rather than becoming cluttered or disharmonious.
  All thirteen Feywild maps request the same seamless loop, so the
  existing audio deduplication keeps it playing through map transitions,
  checkpoint respawns, and reloads without layering or restarting.
- `Feywild 4` (Rootways) is a connected 68x46 east-west forest floor divided
  by giant knotted root masses. Two restrained, gnome-sized redcaps pursue
  Chuck across the broad exposed route, deal 18 Sanity contact damage, and
  take six scratches to defeat, making escape the practical response without
  turning either encounter into a combat gate.
- Reusable low root gaps are ordinary walkable overhead terrain for one-foot
  Chuck but extra-solid terrain for larger pursuers. Redcaps visibly stop at
  the mouth instead of disappearing or teleporting; one gap opens a protected
  refuge and the other is the sole entrance to an optional cigarette-grass
  cache. Rootways has exactly one physical Ashtray, a shared `Feywild 4`
  development checkpoint, reversible travel to Pollen Orchard and Giant Tea
  Table, and the uninterrupted regional soundtrack.
- `Feywild 5` (Giant Tea Table) is a 72x52 enemy-free north-to-south
  exploration respite. A colossal solid tabletop, room-sized plates and cups,
  spilled tea, crumbs, napkins, six chair-leg columns, and four immense table
  legs make Chuck's one-foot scale architectural rather than decorative.
- The required route cannot simply walk around the furniture: dense growth
  closes both side aisles, sending Chuck beneath the table's heavy apron and
  across its cool shadow before the southern clearing. Under-table and apron
  terrain extend the shared large-actor passage rule, while an optional root
  pocket hides one of four cigarette-grass rewards. Two reachable place
  settings offer only the restrained lines `Still warm.` and `Set for one.`
  The map has one physical Ashtray, shared `Feywild 5` development entry,
  Chult-style three-cell edge openings, reversible Rootways and Needle Garden
  travel, and uninterrupted Feywild music.
- `Feywild 6` (Needle Garden) is a 72x50 timing-focused flower maze. Four
  rooted spitting orchids face authored cardinal lanes, remain stationary,
  swell and flash through three readable native-scale frames, then launch hard
  seeds that stop against solid terrain and cost 14 Sanity on contact.
- The opening orchid fires across a broad, safe observation chamber. Later
  orchids occupy narrower flowerbed corridors on evenly staggered cadences;
  the final horizontal/vertical crossing has a lower bypass that replaces
  projectile pressure with the already-established slowing pollen. The
  Ashtray approach never intersects a firing lane. The map has two optional
  cigarette-grass rewards, one physical Ashtray, shared `Feywild 6`
  development entry, reversible Giant Tea Table travel, and uninterrupted
  Feywild music. Its east edge now carries on into the Moonmoth Fen.
- `Feywild 7` (Moonmoth Fen) is a 62x40 wetland of small safe islands strung
  across impassable deep water. Every gap is exactly one tile of the jumpable
  `≈` channel — given new `fey_channel` art here — so each crossing is a single
  committed hop and the fen cannot be walked; two branch islands hang off the
  main chain.
- Lantern moths are the flameskull hazard as living Feywild wildlife: the same
  weaving, unscratchable, 14-Sanity contact behaviour behind a new luminous
  moth sprite with a pale blue wing trail. They haunt fixed horizontal and
  vertical lines out over the deep water, so a crossing means timing the moth
  and the hop together. No landing tile moves. The map has an optional northern
  side island with a cigarette-grass cache, one physical Ashtray, shared
  `Feywild 7` development entry, reversible Needle Garden travel, and
  uninterrupted Feywild music. Its east edge continues into the Warrens.
- `Feywild 8` (Redcap Warrens) is a 76x50 camp map, the region's strongest
  ordinary-enemy area. Four redcaps hold a clearing of gnome-sized gear ---
  kicked-off boots, a cooking cauldron, planted sickles Chuck walks under,
  and crude hide shelters --- standing on trampled camp-dirt terrain so it
  reads as lived-in ground rather than a room. Their notice zones sit more
  than two notice ranges apart, so pursuit never becomes a mob.
- A northern game trail crosses the full width of the map outside every
  notice zone: the warrens are passable without a single fight, while the
  camp centre stays genuinely contested. Solid toadstool thicket walls the
  trail off from the camp, and two Chuck-only openings --- one root arch and
  a pair of toadstool caps --- join them and guard the two cigarette caches.
  No redcap can follow through either.
- Thorn mites are the rat role as fey wildlife: tiny, burr-shaped creatures
  cleared by one committed scratch. They now use the ship-hold rats' exact
  short-notice direct pursuit instead of the sewer rats' fixed patrol. The map
  has one
  physical Ashtray, shared `Feywild 8` development entry, reversible Moonmoth
  Fen travel, and uninterrupted Feywild music. Its east edge continues into
  the Shifting Hedge.
- `Feywild 9` (Shifting Hedge) is a 68x44 ring corridor around a great hedge,
  gated at its four corners. Two gates start open and two start shut. Four
  reactive-flower groups each open one doorway and close another, and every
  group is its own reciprocal, so a second scratch always undoes the first.
  The hedge is fixed and inspectable, never randomised.
- Its two guarantees are proved by walking the entire state space --- every
  tile in all sixteen group combinations. Neither the exit nor the optional
  pocket can be reached without the flowers, and from every state Chuck can
  reach, the exit is still reachable, so no order of scratches can strand
  him. Changes still refuse to land under Chuck, and Sanity-zero restores the
  authored opening state. The map has two cigarette caches in the pocket,
  four thorn mites and no larger enemies, one physical Ashtray, shared
  `Feywild 9` development entry, reversible Redcap Warrens travel, and
  uninterrupted Feywild music. Its east edge continues into the meadow.
- `Feywild 10` (Displacer Meadow) is a 74x48 massive-creature encounter. The
  displacer beast reuses the Chult colossus wholesale behind a new sprite: a
  six-legged blue-black panther with barbed tentacles over its shoulders and
  a faint after-image offset from its real body. It holds the middle of a
  meandering, wholly exposed route thick with slowing pollen, starting far
  enough from the arrival to be seen before it is met.
- The answer is never to fight it. Three walled pockets and four loose root
  arches are built to Chuck's scale: he walks under them and the beast stops
  at the mouth. The Ashtray sits in a pocket a large-actor flood proves the
  beast can never enter, more than a notice range from its haunt, so
  respawning never drops Chuck inside it. The map has two cigarette caches,
  three thorn mites, no redcaps, shared `Feywild 10` development entry,
  reversible Shifting Hedge travel, and uninterrupted Feywild music. Its
  east edge continues into the Underways.
- `Feywild 11` (Mushroom Underways) is a 70x46 recovery map with two new
  terrains: canopy shade, ordinary walkable ground drawn dark and drifting
  with spores, and luminous pools, which are solid so they shape a clearing
  without standing in the way. One rhythm repeats four times --- a long dim
  run under a giant cap, then an open clearing with a pool --- so the walk
  feels like weather rather than a corridor.
- Nothing here pursues Chuck, and that is enforced: no hostile spawn of any
  kind, every enemy list empty at runtime, and a full minute standing still
  costs no Sanity. Between a third and two thirds of everything reachable is
  under a cap, so neither shade nor open ground takes over. The map has three
  quiet side chambers, six fungal tufts holding cigarettes, one physical
  Ashtray under the third canopy, shared `Feywild 11` development entry,
  reversible Displacer Meadow travel, and uninterrupted Feywild music. Its
  east edge continues into the rapids.
- `Feywild 12` (Luminous Rapids) is a 78x44 traversal synthesis with four new
  terrains: fast bright water no one crosses, static wet stepping stones, and
  giant lily pads in risen and furled states. Three crossings run in teaching
  order --- static stones and one-tile jumps first, then two twin pad chains
  where a flower raises one and sinks the other. Each chain fits on one
  screen, so no required landing is offscreen.
- The reactive-flower controller gained a small companion table,
  `GROUP_TERRAIN`, so a group can declare what its change writes. These
  flowers raise and sink pads instead of paving a river with path tiles; the
  default vegetation behaviour is unchanged everywhere else.
- The lower flower is the crossing: a state-space walk with the jump rule
  built in proves the exit cannot be walked to, cannot be jumped to either,
  and that from every reachable state the exit is still reachable. The upper
  flower gates only the north ledge's cache. Pollen thickens approaches and
  never touches a landing tile or a gap; three lantern moths patrol the
  water; one spitting orchid sits on the optional ledge. The map has two
  cigarette caches, one physical Ashtray on the middle isle, shared
  `Feywild 12` development entry, reversible Mushroom Underways travel, a
  connected Map 13 edge, and uninterrupted Feywild music.
- `Feywild 13` (Twilight Crossroads) completes the Phase 9 region with a 76x52
  twilight clearing and several ordinary-looking trails whose connections are
  geographically wrong: leaving the Rapids eastward arrives from the south.
  One reversible flower closes a harmless northern decoy while opening the
  western route, a pollen-heavy direct line offers a slower shortcut, and a
  two-mouth low-root shortcut protects an optional cigarette cache from the
  restrained lone redcap. Five thorn mites provide light wildlife pressure
  without making the route a combat gate.
- The map has one physical Ashtray, shared `Feywild 13` development entry,
  save/Continue and Sanity-zero reset through the existing checkpoint loader,
  and reversible travel to the Luminous Rapids. Its three-cell western
  wilderness opening is deliberately inert: it is the stable boundary for a
  later floating-wizard-tower phase, with no cutscene, tower map, boss, or new
  region transition implemented here. Phase 9's authored content is complete;
  the next pass is the full thirteen-map human acceptance playtest and any
  narrowly evidenced polish it reveals.

## Working systems

- Game loop, native 320x180 surface integer-scaled 4x, scene stack
  with overlay support (dialogue draws over the frozen world)
- Startup now hands off from the one-frame BootScene to a native 320x180 title
  menu. NEW GAME clears the single save slot and loads the authored Waterdeep
  opening; CONTINUE is visibly disabled unless a valid current-version save can
  be restored. A config-gated DEV CHECKPOINTS option opens the temporary test
  selector and disappears entirely when `ENABLE_DEV_CHECKPOINT_SELECTOR` is
  false. The selector pages in twelve-slot screenfuls (session 125): the
  page follows the up/down caret, left/right leap a whole page with
  wraparound, side arrows mark further pages, and a PAGE X OF Y label
  shows the position
- Input: keys -> named actions, normalized 8-way movement vector
- Text maps (assets/maps/): terrain legend + marker system (spawns and
  objects declare their under-terrain); loud errors on any bad data
- Swept, axis-separated tile collision (no tunneling at any dt)
- Smooth frame-rate-independent follow camera, clamped to map bounds
- Sprites from text grids (tools/): Chuck (idle/walk x4 facings), the
  cat, eight human NPCs, and the 75-glyph 5x9 pixel font
- Sanity with i-frames; cigarette pickups; HUD meter (a cigarette
  burning down); patrolling cat hazard; Astral Anchor checkpoints;
  quiet vanish -> starfield -> respawn (no game-over screen, ever); enemies
  rebuild from their map markers when Chuck returns
- Checkpoints and saving: one registry defines map, position/named arrival,
  facing, required progression flags, and visibility/save rules. NEW GAME,
  CONTINUE, and the development selector all call the same
  `CheckpointLoader.load_checkpoint(checkpoint_id)` path. Map-entry definitions
  retain the established local retry behavior; the 29 authored Ashtrays have
  stable IDs and save on first contact. A small version-1 JSON slot under the
  user's application-data folder stores only checkpoint ID, current Sanity, and
  durable progression flags. Invalid, missing, outdated, unknown, or forged
  development-only checkpoint saves disable CONTINUE without crashing. Durable
  flags are `sewer_completed`, which restores the tavern's open exterior,
  `chult_reached`, which restores the playable Chult state,
  `feywild_reached`, which restores the first Feywild riverbank, and
  `crew_pirate_met`, which preserves the first/repeat pirate conversation;
  `captain_chest_opened` preserves the captain chest's opened art and later
  confrontation gate, while `captain_chest_carton_collected` prevents its
  physical golden 40-cigarette carton from duplicating after collection
- Dialogue: JSON data files, typewriter box, eight NPCs; choice
  options can speak, navigate, or close silently
- Audio: pure-stdlib engine (src/audio: synth, instruments,
  sequencer), offline rendering (tools/generate_audio.py +
  tools/generate_music.py <name>), AudioSystem with graceful no-device
  fallback; five composed pieces (data/music/, 7-10 voices) —
  the 95s warm Waterdeep Docks theme and the 83s eerie/funky D-minor
  Sewer theme loop seamlessly, while the 36s one-shot fall-to-Chult cue drives
  the Phase 3 cutscene. Chult now has an original 86s D-Dorian exploration loop:
  a persistent syncopated deep-bass hook, pitched hand drums, woody offbeats,
  layered retro percussion, a compact plucked melody, flute answers, and a humid
  breakdown. It enters immediately on either cutscene arrival or Chult 1 load.
  The Phase 6 entrance hall switches to an original 80s temple loop built from
  low drones, uneven hand drums, dry wood clicks, sparse bells, and restrained
  Phrygian-colored flute phrases. Its sustained voices are mastered to match
  the Chult theme's perceived in-game strength. After direct playtest found the
  matched-RMS mix still too restrained, the temple render alone now uses 0.98
  peak headroom instead of the soundtrack default 0.75 (raised again in
  session 124);
  SFX for pickup, interact, hurt, vanish, respawn, anchor
  chime, a quiet rounded jump bounce, scratch scrape, and per-surface footsteps.
  Re-requesting the same looping track is idempotent, so movement among the
  docks, tavern, and pantry preserves the Waterdeep theme's playback position;
  sewer, cutscene, Chult, and future differently scored regions still switch
  or stop normally
- Distribution: reproducible PyInstaller 6.21 single-file Windows build
  (`CHUCK.spec` + `requirements-build.txt`) bundles all runtime assets and data
  into `dist/CHUCK-demo.exe`. The windowed EXE needs no Python installation,
  excludes unused optional NumPy/OpenGL support, and writes crash diagnostics
  beside itself rather than into its temporary one-file extraction directory
- NPC interaction covers the whole visible person (probe + overlap)
- Depth: barrels/crates are standing props (solid tiles + tall
  sprites), y-sorted with all characters by feet position
- Ground: per-area drawn tilesets (tileset_layout.Tileset: a sheet +
  its terrain rows + char maps; tileset_for(map) picks one) with stable
  per-position variants, animated frames, view culling, and a flat-
  color fallback when a sheet is missing. docks.png, sewer.png, tavern.png,
  pantry.png, chult.png, temple.png, and feywild.png
- Bobert asleep in his barrel at spawn (solid scenery, tile 'B');
  cigarette is a drawn sprite; the Astral Anchor presents as an
  ashtray (cold ash dormant / live ember + smoke when attuned), with
  rect fallbacks for headless runs
- 56x35 map: north warehouse district, tavern front (door 'D', HEROD
  sign 'H'), southeast market with awning 'a' — the overhead layer
  draws canvas over Chuck; flood-fill connectivity is a permanent test
- Prop dialogue: Bobert snores ("... Zzzzz."), the sign reads "Herod
  Cover Band - Tonight Only", and all three northern house doors answer
  "it's closed"; other props are mute; NPCs answer first
- Playtest sizing: human-scale tavern door (now 48x34 with hanging
  lanterns), enlarged west pier (4 rows to col 1), south pier with
  T-head, and a 48-tile market awning
- Tavern exterior: slate roof + chimney props + eave trim + tan brick
  facade + lit windows, all new tileset terrains ('r','e','t','W','m'). It
  begins with solid double doors; returning through the sewer outflow swaps
  them for a 48x34 black open threshold with lit side lanterns. Only the
  threshold tile becomes walkable; the surrounding facade remains solid. The
  freestanding HEROD sign now sits one tile farther west so neither its post nor
  face competes with the open doorway
- District wall: battlements/brick/banners/flickering torches
  ('w','b','F','i') with portcullis gates drawn overhead ('g');
  both northern portcullises now occupy the upper opening row with clear
  walkable stone beneath, so they read as raised/open without changing the
  passage footprint; northern boundary wall battlemented too
- District houses: the three north blocks reskinned with the tavern
  grammar + decorative house doors ('h'); the doors remain solid but are now
  interactable and all return the shared line "it's closed"
- Market stall (cutaway): checkered canopy over the back rows ending
  in scalloped edge ('u') + corner posts ('P'); goods '1'-'5' (produce
  crates/table/barrel) stand visible in the open front row. A human-scale
  market woman stands just left of the goods in a muted headscarf and apron;
  she directs Chuck toward sewer scraps without a quest or marker
- Ruined foundation ('R' walls / 'f' rubble): the mid-map block is a
  crumbling ruin with collapsed gaps; solid, style only
- Breakable grass: three walkable 16x16 tufts frame the ruined foundation and
  four more are scattered through the sewer on ordinary dirt. The shared
  scratch dispatch shreds each into eight radial leaf fragments over 0.42
  seconds and reveals one cigarette at its center. The former exposed
  cigarette south of the ruin was relocated into the first authored reward.
  Grass resets when the map reloads and uses one reusable entity with separate
  stone, dirt, and jungle-ground markers. Eight more tufts are distributed
  across Chult's jungle ground without replacing thorns, enemies, routes, or
  checkpoints. Within two tiles, Waterdeep and sewer reuse the exact
  `Press F to scratch` tutorial line;
  Chult remains prompt-free. Future exterior Chult maps should continue this
  restrained grass scatter through the same shared implementation
- Shared mathutil.approach() (camera follow + any future smoothing)
- Crash logging: unhandled exceptions write crash_log.txt
- Map transitions: WorldScene.load_map(name) (re)builds a whole area;
  a dialogue choice can carry Chuck between maps. Where a choice goes is
  data — a choice option's `goto` names the destination map (no code
  table). Each area's looping music (or deliberate silence) is data too
  (transitions.AREA_MUSIC). Navigation choices can also carry a named arrival
  marker and restrained arrival choreography without hardcoded coordinates.
  The entrance grate's YES drops Chuck straight into the sewer, wordlessly —
  no confirmation lines
- Sewer: assets/maps/sewer.txt is a 48x72, mostly-linear descent
  (walkable corridor wrapped in thick rock so it fills the view) with
  its own tileset (assets/tilesets/sewer.png, built by
  tools/generate_sewer_tileset.py): brick walls '#', stone landing ',',
  dirt 'd', mud 'M', and a drainage channel '%' that flows over 3
  frames. Its own looping theme plays on entry (data/music/sewer.py ->
  sewer.wav). The east-side approach now runs for roughly 28 rows before the
  required jump, with sparse avoidable Astral substitutions foreshadowing the
  wrong map. A hard-edged band of animated dark-blue/purple Astral material
  then interrupts the corridor; SPACE performs a short
  committed hop with a subtle rounded bounce tone that crosses it but cannot
  bypass normal walls. On foot,
  the Astral blocks are a lethal fall zone: control locks, Chuck quietly
  shrinks and sinks for 0.65s, then the existing Astral Anchor respawn
  flow returns him to the sewer entrance. Airborne Chuck crosses safely.
  The nearby jump hint clears after Chuck lands beyond it. Beyond the gap,
  three ordinary rats occupy
  a one-tile choke: their 10x8 sprites are smaller than Chuck, contact
  costs 10 Sanity, and their bodies block progress. F performs a brief
  forward scratch with a moving fan of translucent claw afterimages and
  a brief filtered scrape SFX; one swipe defeats one rat, and the nearby
  tutorial hint disappears when all three are gone. Past the encounter the
  map opens broadly west and continues for another three screens, with Astral
  blocks becoming denser and more chaotically arranged around a continuous
  narrow safe route. Four additional ordinary rats are spaced through this
  late corrupted run; they use the established one-hit behavior without
  extending the original scratch tutorial prompt. Those four make restrained
  six-pixel horizontal patrols at 12 px/s; the three choke rats and any rat
  beside walls, props, another rat spawn, or Astral fall tiles stay stationary.
  Defeated rats reset when Chuck dies and returns. A cold ashtray midway through
  the late maze lights on contact, becomes the active respawn checkpoint, and
  introduces itself on proximity with "Ashtrays save your progress." The safe
  route ends at a three-tile iron drainage outflow drawn overhead from the sewer
  tileset. E opens "Leave the sewer?" with YES/NO choices. NO closes silently;
  YES returns Chuck to the Waterdeep south pier, where he appears one tile out
  in the harbor and rises onto the planks over a restrained 0.65-second
  control-locked climb, with no further dialogue or explanation

- Phase 3 tavern shell: once the sewer return has opened the exterior doorway,
  stepping onto it loads a compact 30x20 tavern common room. A named interior
  arrival places Chuck safely above the threshold facing inward; the matching
  walk-out exit returns him below the Waterdeep doorway facing away, preventing
  immediate transition bounce. The room uses a dedicated procedural tileset;
  its floor now calls the pantry generator's exact worn-board renderer while
  retaining the tavern's distinct interior walls. A bar counter, three
  human-scale tables, chairs, hearth, barrels, and crates remain solid. The
  hearth now occupies the floor tile directly beside the east wall, with no
  intervening plank gap. A small
  raised stage against the north wall uses dedicated top-board and solid front-
  fascia terrain. All remaining floor and the stage's side access form one
  connected traversal area, the camera remains on the normal WorldScene path,
  and the existing Waterdeep theme currently carries across the doorway
- Tavern hook: three non-solid human NPCs use the established dock-worker scale
  and facing/dialogue behavior. The bartender recognizes Chuck and directs him
  to unwanted cheese in the kitchen; a patron supplies one restrained ambient
  line. A third human-height but deliberately thin/lanky musician stands on the
  stage in green clothes and hat with an orange beard and lute, promising 37
  renditions of "Fortune Favors the Kobold." The former common-room cheese trail
  is gone. The north doorway remains plainly open into the pantry without
  requiring an inventory item or flag
- Phase 3 pantry: a compact 26x18 storage room connected bidirectionally to the
  tavern with safe named arrivals. Worn boards, human shelves with jars, sacks,
  barrels, and crates establish the ordinary room before its central broken
  floor. Thirty scattered purple/dark-blue `V` blocks now fracture the ordinary
  boards around the room while reusing the sewer's exact animated Astral art and
  existing fall -> local respawn behavior; small singles and pairs make reality
  feel substituted without breaking the connected safe route. A separate hard-
  edged teal sky with blocky clouds is immediately distinct at native scale.
  Its animation now uses twelve seeded, stable cloud layouts instead of two
  repeated stamps, varying cloud height, width, horizontal placement, and drift
  without rearranging the floor between frames or runs.
  The game's sole cheese sits on a one-board island inside that broad sky field:
  every cardinal approach is four tiles from ordinary floor, beyond Chuck's
  fixed 2.3-tile jump. It is a readable temptation toward the successful fall,
  not a collectible or reachable reward. Approaching within two tiles of the
  teal sky repeats the established `Press SPACE to jump` tutorial line; it is
  absent elsewhere in the pantry and uses the existing temporary hint system
- Fall materials now classify independently before choreography. Astral retains
  its exact fall -> Sanity depletion -> local retry behavior. Teal sky is a
  walkable successful-fall trigger: it begins with the same restrained 0.65s
  shrink/sink animation, preserves Sanity, and replaces gameplay with a
  dedicated `FallingCutsceneScene`. The cutscene has no player-controlled entity
  and fades out the Waterdeep music. After four seconds of exposed freefall, a
  dedicated 36-second one-shot cue launches directly into an urgent D-minor
  pulse, fast bass, melodic runs, and full synthesized kit. It grows chromatic
  and denser as the canopy arrives, fractures at impact, then leaves sparse
  flute, bells, and bass under Chuck's return and cigarette drag. Its complete
  39-second authored visual timeline
  intentionally holds open sky for almost 24 seconds while irregular cloud
  layers scroll upward and the teal grade slowly darkens. Branches, vines, and
  trunks then accelerate through frame as a dense eerie jungle and its ground
  rush upward. Chuck impacts at 29 seconds, quietly blips out through the
  familiar Astral language, blips back, looks left/right/down, places a
  cigarette in his mouth, and takes a restrained smoking drag. Existing scrape,
  thud, vanish, and respawn cues punctuate the collision and return. At 39
  seconds the scene holds on the smoking jungle tableau for two more seconds,
  fades fully to black over 0.75 seconds, then enters playable Chult through the
  shared checkpoint loader. The authored `chult_landing` entry keeps the screen
  black across scene replacement and fades gameplay in over another 0.75
  seconds with control and simulation locked. Direct Chult 1/CONTINUE loads do
  not replay this one-time arrival presentation

- Phase 4 jungle layout: `chult_jungle.txt` is a 64x60 padded playable jungle space
  with a dedicated procedural `chult.png` sheet derived from the cutscene's
  ground, canopy, trunk, vine, and leaf palette. Dense vegetation forms stable
  collision boundaries around the landing and large growth masses create a
  main northbound route with connected side clearings. A central vegetation
  mass near the landing creates an immediate optional left/right exploration
  choice. A three-tile overhead fallen log cuts through a dense wall as the
  first explicit Chuck-sized shortcut: ordinary movement carries Chuck beneath
  the human-scale trunk, which occludes him without adding a crouch control.
  The hidden `chult_landing` runtime
  checkpoint receives the cutscene handoff; the nearby Ashtray is the saveable,
  development-visible `chult_anchor`, displayed as `Chult 1`. Activation saves,
  CONTINUE restores it, and Sanity-zero return uses it. The area is deliberately
  silent until its dedicated Phase 4 soundtrack pass

- Phase 4 undead: two zombies and two skeletons occupy broad Chult clearings,
  never mandatory chokes. Both use the established 16x30 human-NPC scale and
  simple three-facing procedural sprites. A reusable `UndeadEnemy` performs
  direct collision-aware pursuit only within 112 pixels. Zombies shamble at
  18 px/s, inflict 20 Sanity, and take eight scratches; skeletons move at
  25 px/s, inflict 15 Sanity, and take six. Scratch still hits at most one
  target per swipe. Contact blocks Chuck and respects existing damage i-frames.
  Defeated undead rebuild from map markers during the established Astral return,
  alongside cats and rats, while the wide encounter spaces remain escapable

- Phase 4 terrain hazard: 25 thorn tiles occupy six small patches scattered
  through optional clearings, rendered as bright angular stems over ordinary
  jungle ground. A
  reusable terrain-hazard lookup checks Chuck's full footprint rather than a
  Chult-specific scene branch. Contact on foot costs 10 Sanity through the
  established i-frame/hurt feedback; a committed jump passes safely above it.
  Flood-fill coverage verifies the northbound main route remains reachable
  without touching any thorn tile. The former backpack and boot have been
  removed from the northern clearing, along with their unused art and dialogue

- Phase 4 route deeper: a three-tile-wide worn track now leads out of the
  existing northern clearing and terminates beneath a dense canopy arch. The
  walkable threshold carries the named `boundary:chult_deeper` marker. Phase 5
  now binds that existing threshold to `chult_cog`, entering at its safe named
  southern arrival through the ordinary walk-exit/checkpoint path
- Vine-exit readability (playtest, session 109): every hanging-vine jungle
  exit now shows Map 1's worn-trail approach so it reads as "head this way" —
  a short beaten-trail strip before the Chult 2 north exit (one clear row;
  the thorn maze sits directly beneath), the Chult 3 log-crawl approach
  corridor, and the Chult 4 north exit (whose canopy also widened from one
  vine tile to the full five-tile gap). Trail terrain is walkable like the
  ground it replaced, so no route, thorn, grass, or enemy data changed. New
  exits should include a trail approach from the start
- Phase 5 Chult Map 2 foundation: `chult_cog.txt` is an 80x80 authored exterior,
  substantially larger than the 64x60 first jungle. One connected exploration
  network joins a broad southern future-cog clearing, central future-raptor
  territory, and northern future-thorn-maze reserve. It reuses the established
  Chult terrain, dense trees/shrubs, theme, camera, collision, and breakable
  grass language. The shared registry exposes its runtime entry as `Chult 2`;
  no separate debug teleport or new progression flag was added
- Phase 5 sailing cog discovery: a single 224x152 procedural landmark dominates
  the southern clearing. Its shallow diagonal projection sits between the
  game's bird's-eye view and a side elevation: a broad visible deck, sparse
  wooden posts, deep near hull, and sharply tapered southwest bow establish the
  three-quarter perspective. The reference-directed upper silhouette uses one
  wide rectangular cream sail on a plain exposed central mast. The deck remains
  open, with no northwest box, ladder, rigging, or rope details. The mast is
  layered for perspective: the complete sail renders over the rear deck so its
  shape remains uninterrupted and occludes part of the boat, while the lower
  post and broad foot render over both layers, visibly anchoring it aboard.
  Its shaped fourteen-tile-wide solid footprint matches the visible base while
  leaving safe routes around both sides. Twenty-four scattered `V` substitutions arc
  around the hull in small broken clusters, reusing the established animated
  Astral art and ordinary fall/return behavior. They are avoidable on the main
  route, so the ship discovery does not become a mandatory jump gate
- Phase 5 cog sailor: one ordinary human-scale sailor stands visibly on the
  cog's deck in a faded navy coat, weathered trousers, and pale cap. A contained
  elevated-NPC marker preserves the ship's solid hull while painter-ordering
  him over the deck; only his normal interaction zone extends down to the safe
  ground tile beside the hull. From there, the existing dialogue scene delivers
  the three exact sequential boxes: `Oi!`, `Look at that rat.`, and
  `Walkin' on the sea...`. No ship-specific dialogue or teleport path was added
- Phase 5 raptor territory: exactly two large 44x30 Chultan raptors occupy the
  broad central Map 2 clearing, well north of the cog. Their two-frame run,
  30x15 footprint, 68 px/s pursuit, 152-pixel notice radius, and 25-Sanity
  contact make them substantially larger, faster, and more dangerous than the
  prior undead. They are over three Chuck-widths across and more than twice his
  sprite height; Chuck's 80 px/s movement and the clearing's wide side routes
  still leave a narrow, reliable escape advantage. Ten scratches can defeat
  one, but no route or progression state requires either kill. They use shared collision,
  scratch, Sanity/i-frame, painter-order, and enemy-respawn behavior
- Phase 5 massive dinosaur: one 72x60 tyrannosaur-like creature stands alone
  in Map 2's broad northern clearing, separated from the two fast raptors. Its
  reference-informed silhouette uses a huge blunt green head, yellow eyes,
  olive dorsal plates and belly, tiny forearms, heavy legs, and pale square
  claws. A 48x24 footprint reinforces its scale while its 14 px/s pursuit is
  slower than a zombie. Contact costs 40 Sanity and twenty scratches can defeat
  it, but the wide clearing preserves a route around its body and no progression
  state requires combat. It reuses collision, scratch, i-frames, painter order,
  and enemy reset after Chuck's return
- Chult Map 2 now has one physical Ashtray south of the cog. Its hidden
  `chult_2_anchor` save definition is distinct from the development-visible
  `Chult 2` map entry but uses the same registry and loader. Contact saves,
  CONTINUE restores the Ashtray position, and Sanity-zero return rebuilds both
  raptors there. The durable decision log now records one physical checkpoint
  for each newly authored gameplay map
- Phase 5 thorn maze and Chult Map 3 handoff: Map 2's former open northern tip
  is now a compact maze built entirely from established dense-jungle collision
  and 136 existing thorn-hazard tiles. A single southern entrance commits Chuck
  to a substantially longer winding route with multiple safe loops, many branching
  choices, and dangerous thorn-cut shortcuts. A fully thorn-free solution
  remains available without a minimap or unavoidable damage. The
  canopy-framed north threshold transitions to `chult_run` through the ordinary
  walk-exit and named-arrival architecture
- Chult Map 3 undead run: the 48x36 exterior starts quietly at its southern
  Ashtray, then releases three finite groups of 6, 8, and 10 existing zombies
  and skeletons as Chuck advances north. All 24 enemies originate beneath
  flanking canopy arches rather than appearing in open ground, open directly
  onto ordinary notice range of the lane, and funnel into three broad evasion
  spaces. Groups
  release only once, no kill gate exists, and Astral return rebuilds the quiet
  pre-run state. Six reusable grass tufts continue the exterior-Chult convention.
  `Chult 3` remains development-visible through the shared loader; its separate
  physical Ashtray still saves, restores through CONTINUE, and becomes the
  Sanity-zero return point
- Chult Map 3 now ends in a six-tile low passage that Chuck can traverse but
  human-sized undead treat as solid. It leads through the ordinary named walk
  transition into the 64x56 `chult_respite` map without deleting pursuers or
  requiring combat
- Phase 5 Chult Map 4 jungle respite: a mostly calm, lower-pressure exterior
  with dense vegetation masses, 295 authored tree/shrub decorations, a fully
  authored winding route, sixteen shared cigarette-grass tufts, and one
  physical Ashtray. `Chult 4`
  uses the shared development/save loader; the northern Map 5 temple boundary
  is authored but deliberately inert until the next session
- Chult Map 4 stream crossing: a continuous 68-tile animated water ribbon
  winds from the west map edge to the east edge and splits the route into two
  banks. Ordinary movement stops at the water; Chuck's established committed
  jump clears the one-tile crossing. It adds no swimming, drowning, new input,
  tutorial, enemy, or alternate endpoint bypass
- Chult Map 4 northern clearing now contains exactly one reused massive slow
  dinosaur at the open end of the route. Its existing scale, 14 px/s pursuit,
  twenty-scratch durability, 40-Sanity contact, and checkpoint reset remain
  unchanged; the clearing and alternate approach preserve a route around it
- Phase 5 Chult Map 5 temple exterior: a 64x48 enemy-free approach centers a
  huge five-tier stepped pyramid, 42 tiles wide at its base, with 468 solid
  weathered masonry tiles, a six-tile-wide walkable stair, moss/vine variation,
  and a dark readable entrance. Eight grass tufts continue the Chult exterior
  convention. Map 4 now enters its named southern arrival; `Chult 5` and its
  one physical Ashtray use the shared loader/save/respawn path. The entrance
  now hands off into the first Phase 6 interior through a safe named arrival
- Temple approach dressing: four matched pairs of reusable 12x30 skull stakes
  line the path immediately before the pyramid staircase. Their solid native
  footprints preserve an eight-tile central corridor and normal painter order;
  they are mute environmental storytelling rather than enemies or interactables
- Phase 6 Temple Map 1: the former exterior boundary now enters a dedicated
  48x37 monumental entrance hall and can be crossed back without transition
  bounce. Weathered floor slabs, mossy/glyph-marked solid masonry, sparse
  structural piers, and dark thresholds establish a distinct interior visual
  language at native scale. Five matched pairs of animated wall torches now
  establish the recurring temple lighting language. The room is deliberately
  enemy- and trap-free; its
  north doorway is the stable inert boundary for the next dungeon slice.
  `Temple 1` is development-visible, while the room's single physical Ashtray
  saves, restores through CONTINUE, and receives Sanity-zero returns through
  the existing shared checkpoint architecture
- Phase 6 Temple Map 2: the entrance hall's former inert north threshold now
  enters a reversible 48x44 stone corridor without transition bounce or music
  restart. Five full-width rows of large pale spikes divide the route into six
  safe landings. Five durable skeletons occupy alternating landings while
  fourteen animated wall torches reinforce the long, narrow connector shape.
  Spike terrain is solid during ordinary movement and ignored
  only by Chuck's existing committed jump, so each band requires SPACE without
  adding new input, damage, fall, or tutorial systems. The map uses only five
  existing durable skeletons,
  contains exactly one physical Ashtray, exposes `Temple 2` through the shared
  development/checkpoint loader, and connects north to Temple Map 3
- Phase 6 Temple Map 3: a reversible 56x44 chamber continues the temple without
  restarting its music. Twelve existing human-scale skeletons occupy spaced side
  lanes around monumental masonry piers; a connected route still reaches the
  west boundary while reserving a three-by-three avoidance envelope around
  every enemy, so combat is possible but never a progression gate. Twelve
  animated wall torches frame the room, and the former north exit now turns
  west to break the dungeon's straight-line rhythm. The map
  contains exactly one physical Ashtray, exposes `Temple 3` through the shared
  development/checkpoint loader, rebuilds all twelve enemies on Sanity-zero
  return, and turns west into Temple Map 4
- Phase 6 Temple Map 4: a reversible 72x24 west-running connector alternates
  the open skeleton chamber with a long, narrow trap passage. Eight reusable
  wall launchers fire staggered vertical darts through visible timing lanes;
  darts travel faster than Chuck, deal 15 Sanity through normal i-frames, and
  disappear against masonry or after a hit. Eleven animated torches and eight
  dark wall apertures remain visible together at native 320x180. The room is
  enemy-free, contains exactly one physical Ashtray, exposes `Temple 4` through
  the shared loader, resets all active darts on Sanity-zero return, preserves
  uninterrupted temple music, and enters the next open room through its west
  threshold
- Phase 6 Temple Map 5: a reversible 60x44 broad chamber turns the dungeon
  south after the west-running connector. Twenty compact temple snakes occupy
  open looping lanes around monumental masonry piers. They pursue only within
  a finite 96-pixel range, deal 10 Sanity through normal contact/i-frames, and
  intentionally disappear after one scratch. Eighteen animated wall torches
  carry the recurring visual language around the chamber. Combat is not a gate;
  the south threshold remains reachable through connected open space. The map
  contains exactly one physical Ashtray, exposes `Temple 5` through the shared
  loader, rebuilds all snakes on Sanity-zero return, preserves uninterrupted
  temple music, and enters the next narrow map through its south threshold
- Processional path (session 117): the entrance hall's central aisle is a
  four-wide paved walkway ('≡', a new walkable two-variant temple terrain —
  smoother slabs a shade lighter than the floor, with rare worn gold
  flecks) running unbroken from the exterior door to the deeper gate. The
  aisle's three markers (arrivals + Ashtray) declare it as their
  under-terrain, and a test asserts the path spans every aisle row.
  Session 119 extended the language: a short centered stub of the same
  path sits before every other temple doorway (3-wide by up to 3 deep,
  shaped to each door's approach — single-row lanes at the side doors of
  the corridor maps, 2 deep at the snake chamber's south door where a
  snake spawn bounds it). Where a door's approach is a narrow lane (the
  skeleton chamber's west door, the dart corridor's west door), the path
  fills the whole lane and blooms into a full three-tall landing at its
  mouth into the open room; the dart corridor's fully-open east door
  carries a complete 3x3 stub (session 120). Door arrivals/anchors inside
  a stub declare the path as their under-terrain (Ι φ Λ Ρ Η Μ Ζ Σ Ξ), and
  a test locks the per-map path counts (18/23/21/15/18). One Astral scatter cell moved one
  leg south, out of the wind map's east-door stub, preserving the
  36-cell scatter contract and the walk-and-hop course invariant
- Guardian monuments (sessions 115-117, reference-directed): twenty-seven large
  ziggurat statues (48x64 props, two alternating weathering variants each —
  stepped tiers, thin green painted bands, gold diamond plaques, a tiny base
  stair) stand in dense aligned rows through every map with open space: ten
  lining the entrance hall's aisle, five on the spike corridor's landings
  (opposite each landing's skeleton), six in the skeleton chamber's side
  lanes, two between the dart corridor's timing lanes (placed strictly in
  the dart-free columns so no lane gains cover), and four in the snake
  chamber. Only the Astral wind connector stays undressed — its five-wide
  winding passage has no open space to fill. Two faces share the frame: the pale carved skull ('Ϙ'
  anchors) and a coiled serpent with gold-glint eyes and forked tongue ('Ϟ'
  anchors); rows alternate skull/serpent, and the snake chamber's guardians
  are all serpents — its statues match its inhabitants. Each stands on a
  3x2 solid footprint of temple wall cells with the anchor at bottom-center
  carrying the y-sorted prop. Placement was assertion-validated (plain-floor
  footprints, clearance rings free of spawns/thresholds/hazards, full
  connectivity and the entrance's walkable minimum re-verified per statue)
  and a dedicated test locks the per-kind counts, footprints, and row
  formations
- Deeper-door facade (session 114, reference-directed): Temple Map 1's north
  threshold is now a monumental composition — an 80x48 temple_gate prop
  (stepped corbelled crown, tall dark opening, flanking pillars, moss, gold
  diamond glyphs) spanning the walkable doorway, two 28x36 carved-stone
  temple_skull reliefs flanking it on the wall (replacing that wall's two
  idols), and two freestanding pedestal braziers ('ø': a new animated
  two-frame tileset terrain like the wall torch, solid on the floor)
  burning before it. The gate tile ('£', under '∇') transitions exactly as
  the arch char it replaced. The broad chambers carry the language onward:
  skull pairs + braziers on the skeleton chamber's north wall, braziers
  beside the snake chamber's serpent idols
- Temple thresholds: all twelve entrances/exits across Temple Maps 1-6 now use
  narrowed three-tile openings centered beneath reusable procedural stone arch
  props. North/south arches are 48x38 and east/west arches are 38x48, both
  taller than a human NPC and enormous beside Chuck. Continuous dark doorway
  ground replaces the old repeated vertical-frame pattern while the existing
  transition terrain and safe named arrivals remain authoritative. East/west
  arch chars anchor on the BOTTOM row of their three-row openings (props draw
  upward from their tile's bottom edge, so a 48px side arch spans its opening
  exactly from there; a middle-row anchor sits one tile too high — playtest
  caught exactly that misalignment in session 108)
- Phase 6 Temple Map 6: a reversible 48x60 connector winds through four major
  direction changes in a five-tile-wide passage. Eight full-width, one-tile
  Astral Sea cuts require Chuck's established committed jump; stepping onto
  them reuses the quiet Astral fall and checkpoint-return behavior. Session
  118 scattered 36 additional single Astral blocks through the legs — a
  broken-reality fracture that doubles as a harder jump slalom. No scatter
  cell touches a mandatory cut cardinally (nothing widens past the
  ~2.3-tile committed jump), and a permanent test walks the whole course
  with single-tile hops only, proving every safe cell reachable and the
  east boundary attainable. Twenty-seven
  animated wall torches trace the winding route. The enemy-free map contains
  exactly one physical Ashtray, exposes `Temple 6` through the shared loader,
  preserves uninterrupted temple music, returns safely to Map 5, and holds an
  inert east boundary for the next broad room
- Temple interior dressing: all six temple maps carry the game's established
  style-add-on language (the docks' three-quarter buildings, walls/gates, and
  market stall; the jungle's cog, trees, and shrubs) translated into ancient
  temple pieces — coiled serpent idols (26x44, gold-eyed, taller than a human
  NPC), rounded glyph stelae (20x34), terracotta urns (14x18: whole, cracked,
  toppled), and low fallen column drums (24x16). All are mute, y-sorted
  procedural props from tools/generate_temple_props.py with stable positional
  variants. Wall pieces ('†','‡','¦') keep the wall's solidity against its
  face, so no route, torch count, spike band, or dart lane changed; floor
  pieces ('¢','¬') occupy single tiles in the broad rooms only, and a
  dedicated suite locks the per-map placement counts and re-verifies every
  arrival-to-boundary route
- Pantry jar shelves are scratch-breakables (session 112): the two Waterdeep
  pantry shelves build as PantryJarShelf entities. The furniture stands
  forever — solid, human-scale — but one scratch rattles its JARS down into
  glazed ceramic shards and spills a cigarette carton (the same 20-count
  CigaretteCarton the temple urns use). The emptied shelf keeps drawing with
  a dedicated bare sprite (pantry_shelf_empty.png). The scene picks each
  carton's drop tile because only the map knows which neighboring board is
  safe: the left shelf stands directly above an Astral fall tile, so its
  carton lands one tile aside. Shelves restock on reload. The pantry's four
  round floor jars (the 'z' vessels, session 113) are breakables too:
  PantryJar subclasses the temple urn's lifecycle with crockery-toned
  shards — one scratch shatters the jar, clears its tile to open board,
  and spills a carton where it stood
- Temple urns are scratch-breakables (session 110): all 26 dressed urns build
  as living BreakableUrn entities (same positions/variants; idols, stelae,
  and columns stay static). One scratch shatters one urn into terracotta
  shards and spills a full cigarette carton — a new pickup worth exactly
  CARTON_CIGARETTE_COUNT (20) cigarettes (config comment marks the number
  as the contract for the future cigarette counter; sanity simply clamps at
  full today). Wall-base urns spill onto the floor tile beneath them; a
  broken urn's tile clears to its under-terrain through the new
  TileMap.clear_tile, so floor urns open for walking while wall tiles stay
  wall. Urns and tiles rebuild on checkpoint reload like every enemy

- Phase 6 Temple Map 8 (session 122): `temple_gauntlet`, a reversible 40x52
  L-shaped connector where the temple's defenses concentrate — a narrow
  vertical climb crossed by three full-width spike bands with skeletons on
  the landings and a skull/serpent monument pair, turning west into a
  five-tall dart corridor (two down + two up launchers in the dart-free
  pattern) seeded with three single Astral cells. A permanent test proves
  the whole run completable with walking plus single-tile hops. Full kit:
  arches on both doors, paved stubs, braziers at the west boundary (inert
  until Map 9), nine torches, two carton urns, stelae, a fallen column, and
  one shared-loader Ashtray (`Temple 8`). Map 7's north boundary is live
  both ways
- Cigarette counter (session 128): Chuck's coin counter. A CigaretteLedger
  on Game accumulates every cigarette ever collected — loose pickups bank
  one, cartons bank exactly CARTON_CIGARETTE_COUNT (20), settling the
  contract carried since session 110. The total survives map walks and
  Astral respawns (coins surviving a lost life), persists in the save slot
  as a tolerant new field (pre-counter saves stay valid and resume with
  zero; forged/negative totals invalidate the save), restores on CONTINUE,
  and resets only with NEW GAME. Session 129 fixed the fall-to-Chult
  handoff zeroing the count (load_checkpoint now carries the running total
  forward; only NEW GAME and CONTINUE set it explicitly) and added death
  rewind: entering a map or attuning an Ashtray commits the total, and the
  quiet Astral respawn rolls back to the committed value — cigarettes
  gathered past the checkpoint are lost with Chuck. The HUD shows the
  count quietly top-right: a tiny cigarette pictogram beside xN in the
  pixel font, opposite the sanity cigarette. No spending exists yet — the
  ledger only accumulates
- Enemies respect fall hazards (session 127): a shared
  collision.FALL_HAZARD_TERRAIN set ('V', '♠', 's') is extra-solid for
  every pursuing enemy — undead, snakes, raptors, the massive dinosaur,
  and the cat all treat spike pits, Astral cells, and the pantry sky as
  walls, since only Chuck has fall choreography. Skeletons stop flush at
  a band's edge instead of strolling across (verified in the gauntlet:
  20 seconds of pursuit never crosses the row-42 band). Rats keep their
  spawn-validated fixed patrols
- Fall centering (session 126): a fall begins the moment Chuck's
  footprint center crosses a hazard tile, which used to leave his sprite
  mostly over the safe neighbor when entering from the north or a side —
  the sink read as dropping into ordinary ground. The choreography now
  glides him onto the triggering tile's center over the fall's first 40%
  (control is already locked), so he always visibly drops INTO the hole
  from every approach direction, for Astral, spikes, and the pantry sky
  alike. A test enters a cut from the side and asserts the mid-fall
  centering
- Spike pits are fall hazards (session 124): '♠' is walkable now and
  classifies as the exact Astral fall — lethal underfoot with the same
  quiet vanish and checkpoint return, safe only under the committed jump.
  The spike corridor's and gauntlet's bands, and every future pit, share
  one hazard family with the wrong-map material. Tests updated to the new
  contract: walking onto a band is possible-but-death (fall kind
  asserted), safe on-foot floods treat spikes as blocked, and the jump
  suite verifies the hop still clears a band onto safe floor
- Astral wind spike trial (session 124): eighteen spike cells joined Map
  6's course — a mixed spike/Astral trench across the entry chamber (the
  hop lands beside the Ashtray), a full-width band between the final cut
  and the east leg, and nine singles threaded through the leg slaloms.
  The walk-and-hop invariant now spans both hazard kinds: every safe cell
  reachable, the east boundary attainable, single hops only
- Temple loudness (session 124): playtest asked for the temple louder
  again — its render now uses 0.98 peak headroom (RMS ratio vs Chult
  ~1.33; the music suite's band moved to 1.25-1.45 and the temple's peak
  gate to 0.99)
- Shrine hall winding rework (session 123): 150 interior wall cells grow
  two spines out of the shrine hall's monument columns, transforming the
  open room into a wound route — the west entry is forced south through
  the west chamber past its six skeletons, a south gap opens directly at
  the Ashtray, and the central aisle (walled both sides, guardian statues
  embedded in the spines) runs back north to the exit. The east chamber
  becomes an optional pocket entered through a north gap. The envelope
  invariant still holds: entry -> Ashtray -> boundary remains walkable
  with 3x3 avoidance envelopes around every skeleton blocked
- The Astral breach (session 133): once Chuck walks west of
  BREACH_TRIGGER_COL (28) — into sight of the battle — the Astral Sea
  breaks through the sanctum floor behind him (AstralBreach in
  src/entities/battle_hazards.py): a two-tile-thick north-south band of
  'V' terrain at BREACH_COLS (32, 33), landing instantly across the
  rows nearest Chuck so it cannot be outrun, then cascading to the
  walls with a per-tile flash and the vanish sfx. The band is lethal to
  walk into, unjumpable at two tiles, and uncrossable by enemies —
  there is no returning to the east door; the player is sealed in line
  of sight of the fight. A tile never breaks through under Chuck (it
  waits for him to step off). Built on the new TileMap.set_terrain
  runtime mutator; _reset_enemies() restores every mutated tile and
  re-arms the trigger, so death (including falling into the seal)
  heals the floor with the rest of the room. Twenty-four more skeletons
  (Ψ) line the sealed chamber's north and south fringes in two
  staggered rows each (rows 5/7 and 40/42, west of the seal), sparing
  the central sight-line to the beholder and trio: at 7-tile notice
  range they lie dormant until Chuck flees a wall to escape the eye
  rays, then rouse and herd him back to center — 27 skeletons in all
- The beholder boss-battle soundtrack (session 136): the sanctum now
  gets its own climactic theme (AREA_MUSIC["temple_sanctum"] =
  boss_battle.wav) instead of the ambient temple loop. data/music/
  boss_battle.py: an original 80s loop in D Phrygian at 144 BPM, 48 bars,
  11 voices. A relentless choral ostinato (the new ins.choir voice)
  grinds the Phrygian flat-second Eb against a pounding octave bass and
  orchestral timpani (new ins.timpani), while a horn section (new
  ins.brass) soars the theatrical melody over the B section and the coda
  — SNES boss-battle drive with a Duel-of-the-Fates processional menace,
  built from the temple's own D/Eb/C modal world. Dynamic arc: drive →
  soaring B → a dark timpani-roll build → full return → climactic
  turnaround, seamless (loop seam 0.000), rendered at 0.95 headroom to
  match the loud temple/jungle mixes. Three reusable instrument voices
  added to src/audio/instruments.py; tests in test_music.py
- Ship compartment with portholes (sessions 147-148): the playable ship_deck
  (26x13) is an internal wooden hull compartment with brass portholes onto
  the sunlit wavy sea — matching the escape
  cutscene. A dedicated ship tileset (tools/generate_ship_tileset.py ->
  ship.png; tileset_layout.SHIP; MAP_TILESET["ship_deck"]="ship") draws
  plank floor, timber hull wall, and an animated 4-frame porthole tile
  ('Ø', solid) whose sky/sea/crest colours are the cutscene's exact
  palette and whose frames roll the wave crests. Session 148 confined the
  windows to the north hull, added human-scale doors to the side walls, and
  moved Chuck's safe cutscene arrival to tile 13,9 above the new lower-hold
  ladder. This replaced the original plain docks-tileset room/open water band
- Phase 7 opening + lower hold (session 148): the arrival compartment now
  keeps its four animated sea portholes exclusively on the north hull. Its
  west/east walls carry three-cell-tall dark open doorway recesses and the
  south wall carries a 3x2 opening, reserving future interior routes without
  implying that Chuck can operate full-sized doors. A southern floor ladder
  connects
  reversibly to the new 40x30 ship_lower_hold. The hold reuses pantry shelf
  and jar silhouettes alongside crates and barrels; session 150 routed all
  eight shelves and floor jars through the pantry's existing scratch-break,
  debris, tile-clearing, reload-restock, and 20-cigarette-carton lifecycle.
  It houses sixteen ordinary scratchable rats, continues ship_shanty.wav without a
  restart, and owns one physical shared-loader Ashtray plus development-
  visible `Ship Hold`. The user-supplied `docs/design/pirate ship.png` is
  reserved as the composition reference for the later exterior deck map
- Clean cutscene porthole waves (session 150): the Phase 6 escape tableau keeps
  its animated undulating crest/shadow lines but no longer adds four isolated
  white sun-glitter dots inside each porthole
- Walk-in crevice prompt (session 146): the rubble "Enter crevice?"
  YES/NO no longer needs the interact key — walking into the crevice
  zone pops it. ChoiceTrigger gains a walk_triggered flag (a _WALK_TRIGGERS
  set; "crevice"); WorldScene checks walk-triggered zones each frame
  after movement and pushes the choice on entry, with a _walk_choice_armed
  flag that only re-arms once Chuck leaves the zone (so a "NO" isn't
  re-asked while he stands there). Walk-triggered choices are excluded
  from the interact-range check, so the crevice is purely walk-driven
  while the sewer grate keeps its interact prompt
- The ship's pirate theme (sessions 144-145): the escape cutscene and
  the ship deck (the Phase 7 doorstep) share ship_shanty.wav
  (data/music/ship_shanty.py) instead of the borrowed docks loop. Built
  from the docks' fast D-centred groove but turned dark and piratical:
  D MINOR at 126 BPM, 40 bars (~76s), 11 voices. A plucked-fiddle tune
  hammers the classic minor pirate loop (i-bVI-bVII: Dm-Bb-C) and, in
  the turns, the descending Andalusian cadence (Dm-C-Bb-A) with a
  raised-seventh C# for swashbuckler menace; a galloping root-fifth
  bass and bodhran drive it; bold accordion horns (brass), a tin
  whistle, and a gruff crew (choir) chant along in the second half.
  Renders at 0.9 headroom, seamless (seam 0.000), RMS 0.175.
  AREA_MUSIC["ship_deck"] and the cutscene's SEA_MUSIC both play it.
  Tests lock in the minor tonality (F natural, no F#, C# cadence)
- Chaotic collapsed rubble (session 143): the big-block debris was made
  to look like the roof caved in, not tile in rows. temple_rubble_block
  is now 12 variants — each draws one or two chunks at a random offset
  and tumble-rotation (±24°) within a 44x36 canvas (rubble_block seeds a
  per-variant RNG; _stone_chunk lit from above so tilts still read).
  Since props anchor bottom-center per tile, the off-centre chunks break
  the grid alignment, and the per-tile variant index scatters the
  angles. The generator now places debris in irregular collapse-piles
  (a base scatter plus a bonus near ~14 collapse centres) so it heaps up
  in patches and thins between, rather than an even field
- Rubble map rebuilt from big broken blocks (session 142): a new
  temple_rubble_block prop (four chunky 3/4-view broken-masonry sprites,
  tools/generate_temple_props.py rubble_block(); tile 'ß', solid, under
  '·') is now the rubble map's dominant debris. The generator fills the
  chamber with a dense field of these big blocks (~360) plus a scatter
  of smaller column drums (~45) for scale, and the torches, cracked
  stelae, and flat wall-tile boulders were all removed — so it reads as
  one consistent field of collapsed masonry with the clean paved lane
  threading through. temple_column is unchanged, so the temple dressing
  maps are untouched. Rubble test locks in blocks-dominate and no-torches
- Crevice prompt + wordless porthole cutscene (session 141): the rubble
  exit is now an "Enter crevice?" YES/NO interaction (data/choices/
  temple_rubble.json; ChoiceTrigger "crevice"; marker Ҏ on the lane just
  above the ∇ mouth) rather than a walk-over exit — YES routes the goto
  ship_deck through the escape cutscene (intercepted in WorldScene's
  _pending_map handler), NO closes. The escape cutscene lost its
  narration captions (it plays wordlessly), and its emergence tableau
  was rebuilt: a sunlit, lighter-blue sea seen through three round
  brass-rimmed portholes set in the ship's wooden hull wall — plainly a
  ship interior, the sea framed in circles rather than an open breach.
  Suite: test_phase6_escape_cutscene.py (wordless), plus the crevice/
  crawl tests updated to the choice flow
- The escape cutscene (session 140): the Phase 6 -> 7 boundary. Stepping
  onto the rubble crawlspace now replaces the world with
  EscapeCutsceneScene (src/scenes/escape_cutscene_scene.py, a contained
  input-free Scene like FallingCutsceneScene): Chuck crawls a tight stone
  tunnel toward a growing blade of daylight (receding stone rings +
  vignette + scrape sfx), a whiteout, then he emerges into the wooden
  hold with the open sea beyond the hull breach as the sea theme
  (waterdeep_docks.wav) swells in. Three narration captions land the
  moment ("Daylight, at last." / "Salt air..." / "Chuck has reached a
  ship. He does not yet know it."), then it fades and hands off to the
  playable ship deck via load_checkpoint, carrying his Sanity across.
  Suite: test_phase6_escape_cutscene.py; the ship-deck crawl test now
  goes through the cutscene. Phase 6 is content-complete but for its
  distinct boss/cutscene-music polish and Phase 7 gameplay
- The rubble collapse (session 139): temple_rubble was rebuilt to look
  like the temple's ceiling has caved in. The chamber is now choked with
  ~460 pieces of fallen-stone debris (toppled columns '¬' and cracked
  stelae '‡' props scattered at ~58% density off the route, plus lone
  '█' boulders) and split by 15 distinct blocks of Astral Sea (~213 'V'
  cells), making it almost impassable off the path. One intact paved
  lane ('≡', the temple's processional tile — arrival/ashtray unders
  changed to '≡') winds torch-lit from the from_fireball arrival, past
  the ashtray, to the crawlspace mouth: against the debris it reads
  unmistakably as the way out. Generator (tools/generate_temple_rubble.py)
  still asserts the lane connects arrival → anchor → crawlspace on foot
- The rubble crawlspace + the ship deck (session 138): the rubble now
  has its one way out. A narrow crawlspace mouth ('∇') is carved into
  temple_rubble's south wall at the foot of a clear right-side lane
  (tools/generate_temple_rubble.py now protects the lane and proves the
  mouth reachable on foot). Walking onto it (AREA_WALK_EXITS
  ["temple_rubble","∇"]) leads to the new ship_deck map: a 30x18 wooden
  hold (docks tileset — planks, cargo crates/barrels) with a breach in
  the hull opening onto the open sea (water), the Phase 6 → 7 boundary.
  Chuck arrives at the crawl mouth in the deck floor (from_crawlspace)
  and can walk up to the sea reveal. New markers Ҋ/Ҍ; checkpoints
  "Ship 1" (runtime) + "Ship Ashtray"; sea theme (waterdeep_docks.wav).
  No onward exit yet — the escape cutscene (crawl choreography, light,
  the reveal beat) is the follow-up. Suites: test_phase6_ship_deck.py
- The Fireball argument (session 137): the cast is now preceded by a
  dialogue beat. When the survival clock runs out, the camera cuts to the
  battle (reusing the entrance establishing focus) and the adventurers
  argue over the ordinary dialogue box — "you can't cast that here!" /
  "we're too close to an astral rip" / "I have to try" / "......" /
  "FIREBALL!!" (data/dialogue/temple_sanctum.json "fireball_cast").
  Only when the line closes does _begin_fireball fire the blast
  (WorldScene._fireball_dialogue_shown / _fireball_after_dialogue, reset
  with the room). Tested in test_phase6_fireball.py
- The scripted Fireball + the rubble map (session 135): the sanctum
  fight now ends. Once Chuck is sealed in (the breach triggered) and has
  survived BATTLE_FIREBALL_DELAY (24s), the wizard casts Fireball — a
  scripted phase (WorldScene._begin_fireball/_update_fireball/
  _draw_fireball) that freezes the world, blooms an orange-white
  explosion from the wizard into a white-out, shakes the screen
  (FIREBALL_SHAKE) and booms a new deep fireball sfx
  (tools/generate_audio.py sfx_fireball), cuts Chuck to at most half his
  Sanity (FIREBALL_SANITY_FRACTION, never healing), and throws him into
  the new temple_rubble map (fade-in, via the _pending_map path with a
  new _pending_fade_in flag). The survival clock resets with the room, so
  dying before it lands simply restarts the wait. temple_rubble
  (tools/generate_temple_rubble.py, 48x30): a collapsed chamber of 154
  Astral Sea blocks around a clear central spine from the from_fireball
  arrival to the rubble ashtray; temple art/music; new markers Ѣ/Ѥ;
  checkpoints "Rubble 1" (runtime, dev-visible) + "Rubble Ashtray". No
  onward exit yet — the crawlspace and escape cutscene are later slices.
  Suites: test_phase6_fireball.py (6), test_phase6_temple_rubble.py (5)
- Battle chaos (session 134): the sanctum fight was made genuinely
  overwhelming. BattleProjectile now carries a free velocity vector, and
  the ranger whirls (BattleActor.spin, drawn as a rotating sprite;
  BATTLE_RANGER_SPIN_SPEED) loosing a rotating fan of arrows whose aim
  advances BATTLE_ARROW_SPIN_STEP each fast beat — arrows spray every
  compass direction, filling the room. The wizard hurls a westward
  BATTLE_BOLT_FAN of bolts far more often. Rays fire faster. New
  BeholderCone: the beholder occasionally charges a telegraphed wedge of
  force east across the hall (BATTLE_CONE_* — 0.9s pulsing telegraph,
  0.4s lethal window, 216px range leaving an eastern refuge), and on
  detonation the camera shakes (Camera.shake / .offset jitter, decaying
  at CAMERA_SHAKE_DECAY) and a new deep beholder_blast sfx booms
  (tools/generate_audio.py sfx_beholder_blast). BattleChoreographer.update
  now returns a BattleTick(projectiles, cones); the scene tracks
  battle_cones (damage via cone.contains, drawn as a translucent wedge),
  and both reset with the room. Suite: 8 new/expanded tests in
  test_phase6_sanctum_battle.py (19 total)
- The entrance establishing shot (session 133): entering the sanctum
  from the gauntlet queues the heroes' three lines at the far-east door,
  ~40 tiles from the battle. The camera now cuts to the fight for those
  lines (Camera.focus_on holds a fixed point while the dialogue freezes
  the world) so they land on the trio, not the empty aisle, then hard-
  cuts back to Chuck when the conversation closes
  (WorldScene._battle_establishing_focus centers on the actors' span and
  lifts their feet clear of the dialogue panel; SANCTUM_ESTABLISH_LIFT).
  The trio was reclustered into a tight arc around the beholder — ranger
  (18,20), fighter (16,22), wizard (19,25), beholder (10,23) — so all
  four frame in one shot; the ranger and wizard were the old vertical
  outliers (rows 15 and 26). The aisle path (138 ≡) is untouched
- The battle in motion (session 132): the sanctum tableau now fights on
  fixed cadences Chuck cannot influence (src/entities/battle_hazards.py).
  The beholder's eye rays cycle the three adventurers' lanes in a
  learnable order and dissipate at BATTLE_RAY_RANGE (320px), keeping the
  arrival aisle survivable; the ranger's arrows and the wizard's bolts
  streak west at the beholder and die on the west wall; the fighter's
  slash pulses west of him where three new skeletons (ordinary Ψ
  markers, the room's only conventional enemies) press his line. Every
  attack is a BattleProjectile or slash zone that costs Sanity through
  the ordinary i-frame path; the shot is spent on impact. The
  BattleChoreographer rebuilds with _reset_enemies(), so death restarts
  the cadences and re-presses the skeletons. Actors animate in place:
  the beholder's hover breathes on a sine, adventurers sway on offset
  phases, and each actor lunges toward its target for a beat
  (attack_flash) when its attack fires. Suite:
  tests/test_phase6_sanctum_battle.py (7 tests)
- Battle tableau, first slice (session 131): four procedural actors hold
  the sanctum's western arena as static y-sorted presences — the armored
  fighter (16x30, sword and shield), the blue-robed wizard (gem staff),
  the clearly female ranger (long auburn ponytail, longbow), and the
  beholder (40x40, five eye stalks, one vast glaring eye, floating on a
  hover offset over a ground shadow). Entering from the gauntlet plays
  three heroic non-interactive entrance lines (data/dialogue/
  temple_sanctum.json) through the ordinary dialogue box before control
  returns. The actors answer nothing: E gets no response, scratches pass
  through them, their identities are never explained (phase contract).
  Combat behavior, attacks, and the Fireball are the next slices
- Phase 6 Temple Map 9 (session 130): `temple_sanctum`, the final chamber
  structurally — the temple's widest hall (64x48, 2032 walkable tiles). A
  138-cell paved processional runs from the east door (the room's ONLY
  threshold; per the phase contract the scripted Fireball, a later slice,
  is the only way onward) between eight alternating guardian colonnade
  monuments to the western dais, where carved wall skulls and six braziers
  stage the coming battle. Fourteen torches, three carton urns, four
  stelae, two fallen columns, one Ashtray (`Temple 9`), reversible
  east-door transitions with the gauntlet (whose west boundary is now
  live), and deliberately no enemies and no onward exit — the
  adventurers/beholder battle and Fireball are their own next slices
- Phase 6 Temple Map 7 (session 121): a reversible 56x44 shrine hall east
  of the Astral wind connector, entered through a west-wall arch onto a
  full-width paved landing. Twelve avoidable skeletons occupy the side
  lanes (a permanent test proves every tile reachable even with 3x3
  avoidance envelopes around all of them); four skull and four serpent
  guardian monuments flank the aisle to the north door, which carries the
  full threshold kit — arch, path stub, flanking braziers and carved
  skulls — and stays inert until Map 8. Breakable urns, stelae, a fallen
  column, twelve torches, one physical Ashtray (`Temple 7` via the shared
  loader), uninterrupted temple music, and both-ways transitions with
  Map 6 (whose formerly inert east boundary is now live)
- Phase 4 dense vegetation art: the former blocky green collision texture is
  now an interlocked organic canopy of broad leaves, woody seams, and hanging
  vines. Across the same solid vegetation cells, deterministic y-sorted
  tree props use three 34x46 silhouettes with layered tropical crowns, trunks,
  and trailing vines. A second solid vegetation decoration adds broad-leaf
  shrubs across the same masses using three 28x24 variants: overlapping pointed
  leaves, central veins, and brighter tropical midtones. Trees rise above human
  NPC height while shrubs are wider than two Chucks, making each collision mass
  read as dense forest and understory without changing a walkable tile or route
- Jungle densification (session 111): all five Chult exteriors gained new
  organic vegetation blobs (~8-10% of each map's plain open ground — 576 new
  cells total: 172/211/29/69/65) so the jungle presses closer around the
  routes. New masses use the same canopy terrain studded with trees and shrubs
  at the established session-73 density. Placement was generated under strict
  guards: 2-tile buffers around every spawn/marker/special terrain, full
  walkable connectivity (the stream treated as jump-crossable) re-verified
  after every blob, the undead run's central lane excluded, the respite's
  bank-size minimums held, and the cog's raptor-notice-radius bypass route
  preserved. The Chult 1 tree/shrub test band widened (150-240/160-240) to
  cover the larger mass area

## Placeholder systems
- Phase 4 previous-traveler evidence needs a replacement environmental scene
  after the requested backpack/boot removal; all other authored feature slices
  remain pending full-route human playtest and acceptance
- (Quiet music variation cut by creative direction — soundtrack is
  Phase-One-complete)

## Known issues / accepted quirks

- E and RETURN interact; SPACE jumps. The jump is intentionally short;
  Astral material is safe only while Chuck is airborne.

- Scroll shimmer fix (session 29): native pipeline audited whole-pixel
  (int camera offset used by every draw; exact 4x nearest-neighbor
  scale). Cause was at presentation: Windows DPI scaling stretching
  the DPI-unaware window non-integrally (+ possible tearing). Fixed
  via SDL_WINDOWS_DPI_AWARENESS=permonitorv2 and vsync=1 (best-effort).
- Stop-shake fix (session 30): vsync + clock.tick double-pacing made
  dt oscillate, which showed as +/-1px lurches during the camera's
  asymptotic settle tail. Fixed by clamping dt (MAX_DT = 1/30) and
  snapping the camera to target within 0.5px so the settle ends
  crisply instead of hovering at a rounding boundary.

- NPCs are intentionally not solid (Chuck walks between boots)
- The world freezes entirely under dialogue (deliberate)
- Docks map bottom rows are open water with no southern content

## Tests

80 standalone suites (most pure Python/headless) cover the shared engine and
content from Waterdeep through the complete thirteen-map Feywild region. The
Phase 9 coverage includes every map transition and development checkpoint,
reactive-flower state and reset guarantees, pollen, Chuck-only passage
blocking, enemy roles and reset, save/Continue/respawn, uninterrupted music,
and the inert final boundary. All 80 pass, compilation is clean, and the dummy
SDL launch reaches `TitleScene` after the boot frame.

## Phase 2 progress (starting area + sewer tutorial)

1. [x] Waterdeep guard: armored NPC at the upper plaza's east edge,
       "Stick to the docks, rat." No gate/barrier — the map layout
       already blocks (sessions 32-33)
   - [x] Market woman: human-scale NPC beside the open market goods,
         "No handouts here. If you're hungry, you should check the sewer for
         scraps" with no quest, marker, or waypoint (session 51)
2. [x] Tutorial text ("Press E to interact"), area-scoped, shown only
       while an interactable is in reach (session 34)
3. [x] Sewer grate + Yes/No dialogue choice: choices are data
       (data/choices/*.json), DialogueScene renders options with a
       caret, up/down selects, E commits; YES enters the sewer and NO
       immediately closes with no follow-up text (sessions 35/48)
4. [x] Sewer map + tileset: the grate's YES loads a narrow, linear
       sewer map (assets/maps/sewer.txt) via a reusable
       WorldScene.load_map + data-driven `goto` (sessions 36-37). Now
       with its own art (assets/tilesets/sewer.png): brick walls, stone
       landing, dirt/mud, and a flowing drainage channel. Per-area
       tilesets (tileset_layout.Tileset + tileset_for). YES is wordless
5. [x] Sewer music: an eerie/funky 83s D-minor loop (data/music/sewer.py,
       rendered to sewer.wav), wired via AREA_MUSIC and playing on entry
       (session 38)
6. [x] Astral Sea glitch blocks + jump mechanic & tutorial: animated
       dark-blue/purple wrong-map tiles form a one-tile fall-death zone;
       SPACE makes a restrained forward hop, a failed crossing plays a
       shrink-and-sink fall before normal respawn, ordinary walls remain
       solid, and the hint clears after landing beyond it (sessions 39/41)
7. [x] Rats + scratch attack & tutorial: three smaller ordinary rats
       physically block a narrow post-gap choke; F makes a brief forward
       motion-blurred swipe with a dry scrape SFX, one hit removes one rat,
       contact costs light Sanity, and the proximity hint clears with the
       group (sessions 40/42)
   - [x] Sewer route expansion: longer pre-gap walk with sparse Astral
         foreshadowing, then a broad westward post-rat continuation with
         escalating corruption and a preserved safe path (session 43)
8. [x] Sewer exit -> climb-out -> return to docks: a rat-scale iron outflow
       uses a data-driven YES/NO interaction and named south-pier arrival;
       NO closes silently, while YES has Chuck rise one tile from harbor water
       onto the planks in a brief, silent, control-locked animation. The late
       maze now also contains an ashtray checkpoint with proximity guidance
       (sessions 47/50)
9. [x] Tavern doorway opens (Phase 3 setup): the initial solid doors remain
       until Chuck returns through the sewer outflow, then become a dark,
       walkable exterior threshold. No interior or Phase 3 transition is
       present (session 52)
10. [x] Added reusable scratchable grass: three tufts around the ruined
        foundation and four through the sewer. Their brief leaf-debris animation
        reveals cigarettes, while a two-tile Waterdeep/sewer-only proximity hint
        repeats `Press F to scratch` (sessions 76-77).

## Next recommended session

Run the Phase 9 full regional acceptance playtest from `Feywild 1` through
`Feywild 13`, then load each development checkpoint individually. Keep any
follow-up strictly to issues observed during that playtest; do not begin the
floating wizard tower without its own phase document.

## Also open

- Full Phase 2 human playtest and acceptance
- Dedicated tavern music or ambience (the shell currently reuses Waterdeep)
- Full clean-start Phase 3 human playtest and timing acceptance

## Phase 4 progress (Chult jungle)

1. [x] Phase 4 contract added and made the active development scope.
2. [x] Phase 3 tableau now hands control to a first playable Chult landing map
       through `load_checkpoint("chult_landing")` (session 64).
3. [x] First procedural Chult terrain sheet matches the cutscene palette and
       supports stable jungle-ground and dense-vegetation collision language.
4. [x] `Chult 1` Ashtray is wired to save, CONTINUE, development selection, and
       Sanity-zero respawn through the existing shared architecture.
5. [x] Expanded 64x60 padded connected exploration layout with a main route, optional
       branch, and overhead fallen-log passage sized for Chuck (session 65).
6. [x] Added two human-scale durable zombies and two skeletons with simple
       collision-aware pursuit, avoidable placement, existing scratch/contact
       damage, and Astral-return reset behavior (session 66).
7. [x] Expanded the reusable thorn terrain to 25 tiles across six optional
       patches: 10 Sanity on-foot contact, existing i-frames, jump-safe
       traversal, and a safe main route around every patch (sessions 69/75).
8. [ ] Add replacement previous-traveler evidence after the requested removal
       of the backpack and boot (session 75).
9. [x] Added a clear worn north trail and canopy-framed, named
       `chult_deeper` boundary without inventing the next full map (session 71).
10. [x] Added an original 86-second bass-forward Chult exploration loop with
        syncopated percussion, layered groove, melodic identity, clean looping,
        and normal area/checkpoint audio integration (session 72).
11. [x] Replaced block-like dense-jungle art with organic canopy texture and
        165 oversized tree silhouettes while preserving collision and routes
        (session 73).
12. [x] Added 170 deterministic broad-leaf shrub props across remaining solid
        vegetation cells, with three procedural variants and no route changes
        (session 74).
13. [x] Scattered eight reusable breakable-grass tufts across ordinary jungle
        ground and established them as an exterior-Chult map convention without
        extending the Waterdeep/sewer scratch tutorial (session 78).

## Phase 5 progress (deeper into Chult)

1. [x] Added the Phase 5 contract and made it the active development scope.
2. [x] Added the 80x80 connected Chult Map 2 foundation, linked the established
       Phase 4 north threshold to its named southern arrival, reused the Chult
       tileset/theme, scattered ten shared grass tufts, and registered `Chult 2`
       through the shared checkpoint loader (session 79).
3. [x] Added the oversized three-quarter-view sailing cog landmark, shaped
       solid hull footprint, and 24 avoidable animated Astral Sea substitutions
       around its base while preserving safe routes on both sides (sessions 80-84).
4. [x] Added a human-scale sailor visibly on the solid cog deck, reachable from
       safe ground and using the exact three sequential dialogue boxes through
       the existing dialogue system (session 85).
5. [x] Added exactly two large, fast, scratchable raptors in the broad central
       encounter space, with avoidable finite pursuit and normal respawn reset.
       Added Map 2's single physical shared-loader Ashtray (session 86), then
       enlarged the raptors and increased pursuit speed (session 87).
   - [x] Added one reference-informed massive but slower dinosaur in the broad
         northern clearing, with optional combat and normal reset (session 88).
6. [x] Added a compact branching thorn maze with a safe solution, transitioned
       it into a connected Chult Map 3 staging foundation, and added Map 3's
       shared development entry and one physical Ashtray (session 89). Increased
       the maze to 136 thorns, one entrance, a longer route, and more difficult
       loops and wrong turns after playtesting (session 90).
7. [x] Added three increasing, finite undead releases from readable jungle
       openings, preserving a run-through route, ordinary combat, and complete
       encounter reset at the Chult 3 checkpoint (session 91), then expanded
       the authored groups to 6/8/10 undead after playtesting (session 92).
8. [x] Added a six-tile Chuck-sized escape that blocks human-sized undead, then
       transitioned into a lower-pressure 64x56 Chult Map 4 with dense
       vegetation, a deliberately meandering route, sixteen grass tufts, no
       enemies, one physical Ashtray, and shared `Chult 4` development loading
       (session 93).
   - [x] Added a map-spanning animated jungle stream with one required jump
         crossing, using the existing jump/collision behavior (session 94).
   - [x] Added one existing massive slow dinosaur to the broad northern
         clearing while preserving an optional route around it (session 95).
9. [x] Added the 64x48 Chult Map 5 exterior with a dominant five-tier stepped
       pyramid, broad walkable stair, dark inert dungeon boundary, eight grass
       tufts, no enemies, shared `Chult 5` development loading, and one physical
       Ashtray. Connected Map 4 through its existing named boundary without
       beginning the dungeon (session 96).
   - [x] Lined the pre-stair approach with eight reusable, human-scale skull
         stakes while preserving the broad central route (session 97).

## Phase 6 progress (jungle temple)

1. [x] Added the Phase 6 contract and made it the active development scope.
2. [x] Connected the Map 5 pyramid entrance to a reversible 48x37 Temple Map 1
       entrance hall with dedicated procedural interior art, one physical
       shared-loader Ashtray, development-visible `Temple 1`, and an original
       80-second ancient/shamanic exploration loop (session 98).
3. [x] Added a reversible 48x44 Temple Map 2 with five mandatory one-tile
       spike-pit jumps, five skeletons on alternating landings, fourteen wall
       torches, dedicated temple art, uninterrupted temple music, one
       physical shared-loader Ashtray, development-visible `Temple 2`, and a
       north boundary leading into the next room (session 101).
4. [x] Added a reversible 56x44 Temple Map 3 with twelve durable skeletons in
       avoidable side lanes, broad looping routes, twelve wall torches,
       uninterrupted temple music, one shared-loader Ashtray,
       development-visible `Temple 3`, and a west boundary entering the next
       narrow connector (sessions 102-103).
5. [x] Added a reversible 72x24 Temple Map 4 west-running connector with eight
       staggered reusable dart launchers, eleven wall torches, one physical
       shared-loader Ashtray, development-visible `Temple 4`, uninterrupted
       temple music, and a west boundary now connected to the next open room
       (session 104).
6. [x] Added a reversible 60x44 broad Temple Map 5 with twenty one-hit snakes,
       looping lanes, eighteen recurring wall torches, one physical shared-
       loader Ashtray, development-visible `Temple 5`, uninterrupted temple
       music, and an inert south boundary for the next connector (session 105).
7. [x] Reworked all Temple Map 1-6 thresholds into human-scale procedural stone
       arches over narrowed three-tile openings, then added a reversible 48x60
       Temple Map 6 winding connector with eight mandatory Astral Sea jumps,
       twenty-seven wall torches, one shared-loader Ashtray, development-visible
       `Temple 6`, and an inert east boundary (session 106).
8. [x] Dressed all six temple interiors with the established style-add-on
       language: serpent idols, glyph stelae, terracotta urns, and fallen
       column drums — 54 mute y-sorted procedural props that change no route,
       count, or hazard, locked by a dedicated test suite (session 107).
9. [x] Added the reversible 40x52 Temple Map 8 gauntlet: spike climb,
       dart corridor, Astral seeds, monument pair, full kit, one
       shared-loader Ashtray, and an inert west boundary for Map 9
       (session 122).
10. [x] Completed the multi-map dungeon, final battle, Fireball transition,
        rubble crawlspace, wordless escape cutscene, and ship arrival across
        bounded slices (sessions 130-147).

## Phase 7 progress (pirate ship)

1. [x] Added the Phase 7 contract and made it the active development scope.
2. [x] Corrected the existing arrival compartment to use four north-wall-only
       animated portholes, human-scale dark open doorway recesses on the other
       walls, and a southern floor ladder while keeping the established Phase
       7 ship theme continuous (sessions 148-149).
3. [x] Added the reversible 40x30 lower hold with pantry-derived breakable
       shelves/jars that spill 20-cigarette cartons, crates, barrels, sixteen
       ordinary rats, one physical Ashtray, and
       development-visible `Ship Hold` through the shared checkpoint loader
       (sessions 148/150). The hold rats now use the temple snakes' 96-pixel
       notice-and-chase pattern at 32 px/s, with swept wall/fall-hazard
       collision and the existing one-scratch defeat/contact-Sanity behavior.
       Sewer rats retain their established short patrols, and death/reset
       restores all sixteen hold pursuers (session 169).
4. [x] Added a reversible 40x26 working galley through the arrival room's west
       open passage, with counters and storage forming escape lanes, one
       physical Ashtray, development-visible `Ship Galley`, and uninterrupted
       shanty playback. The human-scale chef delivers the exact authored line,
       then starts a collision-aware 58 px/s cleaver chase; his two-frame
       directional run/swing animation is richer than ordinary NPCs, contact
       costs 20 Sanity, and death rebuilds and re-arms the encounter. He is
       intentionally not scratchable, keeping this an escape slice (session
       151).
5. [x] Added reversible 42x30 crew quarters through the arrival room's east
       open passage: eight hanging human bunks, an oversized round mess table,
       cargo, one physical Ashtray, development-visible `Ship Crew Quarters`,
       and uninterrupted shanty playback. The seated pirate has a restrained
       two-frame mug/sway animation and distinct first/repeat dialogue; meeting
       him sets the durable `crew_pirate_met` flag, which survives checkpoint
       save and CONTINUE. Its open captain-cabin route and deck ladder now lead
       to their completed destination maps (sessions 152-154).
6. [x] Added a reversible 36x26 captain's cabin through the crew room's open
       east doorway, with north-wall portholes, oversized human furniture, one
       physical Ashtray, development-visible `Ship Captain Cabin`, and the
       uninterrupted shanty. Its two-frame brass-bound chest grants Premium
       Buhetian Halfling Leaf (+40 cigarettes) once, switches permanently to
       an open/empty interaction, banks the paired reward against death, and
       persists both flag and count through save/CONTINUE (session 153).
7. [x] Added the reversible 64x44 exterior deck through the crew ladder, using
       the authored pirate-ship image as its composition reference: a broad
       tapered hull, two large mast-and-sail silhouettes, animated line-wave
       ocean, one physical shared-loader Ashtray, development-visible `Ship
       Exterior Deck`, and uninterrupted shanty playback. The ocean remains
       visually fixed while the complete ship/occupant layer rocks by one
       pixel over an eight-beat 126-BPM cycle; collision stays stable. The
       deck cast and ending sequence remain deliberately unbuilt (session 154).
   - [x] Enlarged both mast-and-sail props to a ship-scale 144x136 silhouette
         and aligned their anchors east-to-west along the deck's exact center
         row, replacing the small diagonal arrangement (session 155).
   - [x] Narrowed the hull's north-south beam from 30 tile rows to 22 without
         shortening it, moved the hatch/Ashtray safely inward, and enlarged
         both centerline mast-and-sail silhouettes again to 176x160 (session
         156).
   - [x] Enlarged both centerline mast-and-sail silhouettes to a deck-spanning
         224x192 and added a dedicated 120x32 east-facing bowsprit that plants
         inside the bow rail and projects over open water (session 157).
   - [x] Rebuilt the bowsprit as a massive 400x96 structural spar with over
         twelve tiles of visible projection, and moved its reinforced heel
         onto the actual eastern bow-edge rail tile (session 158).
8. [x] Populated the deck with its four non-combat performers: a concertina
       player with expanding bellows, a cheering tankard pirate, a four-step
       dancing pirate, and Jeffries visibly struggling in rope against the
       main-mast pole. Each uses four directional frames advancing on
       half-beats at the shanty's 126 BPM, distinct first/repeat dialogue, and
       a durable save flag. Jeffries delivers the authored collided-world
       warnings while the cheering pirate dismisses him. The fencing hazard
       and ending sequence remain deliberately unbuilt (session 159).
   - [x] Replaced the animated crew's full-width side-view tricorn rectangles
         with stepped crowns and narrow brims. Left/right dialogue facings now
         preserve readable eyes, noses, cheeks, and hat bands at native scale;
         the shared procedural fix covers the four performers and captain
         without changing their front/back art or interactions (session 171).
   - [x] Lifted Jeffries' rendered struggle fully onto the mast pole while
         preserving his accessible interaction tile, and added a human-scale
         procedural helm immediately sternward of the main mast (session 161).
   - [x] Corrected the helm to the masts' east-west centerline and redrew its
         wheel in a strongly foreshortened transverse plane for the ship's
         starboard three-quarter viewpoint (session 162).
9. [x] Added two human-scale sword-fighting pirates to the central deck lanes.
       Their paired controller wanders a shared midpoint while the fighters
       guard, lunge, high-parry, and recover on opposing shanty half-beats;
       swept tile collision keeps them off masts and rails. Contact costs 15
       Sanity, broad routes remain open above and below them, and ordinary
       death reset restores the complete pair. They are an avoidable hazard,
       not a combat gate or scratch target (session 160).
10. [x] Added a durable seven-condition captain gate covering the galley chef,
        seated pirate, four deck performers, and one-time chest reward. Once
        complete, the captain emerges at the midship ladder with a dedicated
        four-frame walk cycle. The camera follows his clear route north of the
        Ashtray and west to the stern helm, where the nearby concertina crewman
        turns toward him and announces `Captain on deck!`. Two restrained
        `...` dialogue beats pace his accusation, plank order, the crew's exact
        authored objection, and refusal. Completion saves at the deck Ashtray
        and CONTINUE restores the captain without replaying the exchange
        (sessions 163/170).
11. [x] Added a staged eight-tile starboard plank that replaces one rail
        section and projects as a narrow walkable strip over animated ocean.
        After the confrontation, the captain and objecting pirate flank the
        approach while Chuck begins an input-locked, normally animated
        wooden-footstep walk. The sequence no longer returns control at the
        rail: Chuck steps onto the plank, pauses for Jeffries' warning, then
        automatically walks to its outer tile and flows directly into the
        captain's approach, kick, and Hell fall. Saved confronted state still
        restores the complete tableau without replaying the procession.
   - [x] Restored the arrival compartment's unused south doorway to ordinary
         solid hull, leaving only its three real routes. Replaced the captain
         chest's direct dialogue reward with a four-frame opening action
         triggered by interact or scratch; it now drops a physical golden
         40-cigarette carton in front, banks the reward on collection, and
         restores opened/uncollected/collected states without duplication
         (session 165).
   - [x] Added reusable approach confirmations to all four live ship ladder
         directions. The hold descent and exterior-deck return ask
         `Climb down ladder?`; the hold return and crew-to-deck route ask
         `Climb up ladder?`. YES uses the existing AreaExit destination,
         named arrival, and facing; NO closes silently and stays dismissed
         until Chuck leaves and reapproaches the ladder (session 166).
   - [x] Rebuilt every ship ladder from a repeated 16x16 icon into one
         continuous 16x32 top/bottom structure, matching the established
         16x30 human NPC sprite scale. Both walkable halves share the same
         YES/NO transition, and nearby named arrivals were kept safely off
         the enlarged footprint (session 167).
12. [x] Added a deterministic moving reality field that activates when Chuck
        automatically steps onto the staged plank. Eight staggered Astral and
        volcanic Hell fragments enter from the native screen's east edge,
        travel fully clear of its west edge, and recycle continuously to sell
        the ship's forward motion. Astral chunks tile the exact animated
        `astral_void` fall-hazard cells shared by the sewer, pantry, Chult, and
        temple rather than using a separate approximation. Hell chunks now
        read as a bird's-eye plane below the ship: dark irregular basalt
        shelves cover flowing orange lava channels, angular fissures, exposed
        pools, and pinprick molten vents, with no side-facing flame edge. Their
        layouts use seed-varied row heights, staggered origins, slab sizes, and
        gaps so neighboring fragments do not align into a uniform lava grid;
        the deterministic terrain remains stable while only heat highlights
        animate. The streams render behind the hull/plank, remain non-colliding,
        and the endpoint still prevents the unbuilt kick/fall from beginning
        early. Jeffries retains his one-time `It's back! The purple is back!`
        warning (sessions 168/172/173/174).
13. [x] Completed the Phase 7 endpoint. Reaching the outer plank tile locks
        control and sends the captain along the authored plank centerline
        behind Chuck. He waits for an actual streamed Hell fragment to cross
        beneath the endpoint, extends a readable boot with impact feedback,
        and knocks Chuck into that same moving fragment while Chuck shrinks
        through the established fall animation. A dedicated input-free Nine
        Hells descent reuses the fall-to-Chult cue and its four-second music /
        29-second impact timing language, replaces clouds and jungle with
        rising volcanic fragments, sparks, and an approaching overhead
        basalt/lava plane, then holds on Chuck's arrival without granting
        gameplay control. This is the stable Phase 8 boundary; no Phase 8 map,
        mechanics, checkpoint, or narrative content was invented (session
        175).
   - [x] Added the development-only `Captain Arrival` checkpoint through the
         shared checkpoint registry/loader. It enters the exterior deck with
         all seven production prerequisites and without `captain_confronted`,
         so the ordinary gate starts the captain walk on the next update
         (session 176).
   - [x] Fixed the crew-quarters ladder crash by keeping `Captain Arrival`
         development-selectable but excluding it from ordinary named-arrival
         resolution. The ladder now resolves uniquely to the normal exterior
         deck entry, while direct development loading still starts the captain
         sequence through the same checkpoint loader (session 177).
   - [x] Enlarged all ship hammocks from 20x34 to 30x44 native pixels, then
         added a 72x44 solid captain's bed and an 80x48 central woven rug to
         the captain's cabin. The rug uses a reusable flat-prop layer so Chuck,
         furniture, and pickups always draw above it (session 178).
   - [x] Compressed only the north-south spans of the galley (40x26 -> 40x22),
         crew quarters (42x30 -> 42x24), and captain cabin (36x26 -> 36x21).
         East-west lengths, props, enemies/NPCs, ladders, open passages,
         arrivals, Ashtrays, chest behavior, and reversible routes remain
         authored; moved Ashtray checkpoint coordinates match their new rows
         (session 176).
   - [x] Removed the remaining solid near-black up-facing deck-pirate head
         patch at its procedural source and regenerated all five affected
         sheets with warm shaped head/scarf silhouettes (session 176).
   - [x] Replaced the remaining full-width rear tricorn rectangles in both
         captain/deck and seated-pirate generators with narrow peaked
         silhouettes. Up-facing performance and captain-walk frames now retain
         readable warm head/scarf pixels at 4x scale (session 179).
   - [x] Widened the staged starboard gangplank from one tile to two (16px to
         32px), including its rail opening and collision. Either lane starts
         the reality warning and endpoint sequence; the cinematic recenters
         Chuck and the captain on the broad plank before the kick. Its
         procedural tile now fills both halves without a water seam (session
         180).
   - [x] Revised the Nine Hells fall so no overhead Hell tiles appear behind
         Chuck in the street-view descent. A large distant volcano now anchors
         the open heated sky. The landing plane is over 90% basalt with sparse
         molten fissures. On impact Chuck now follows the Chult landing's exact
         quiet death timing: a `hurt` beat, vanish at 29.15 seconds through the
         same contracting Astral-star blip, respawn at 31.1 seconds through the
         same return flicker, then the established left/right/down look,
         cigarette insertion, ember, drag, and smoke before the playable
         Phlegethos handoff.

## Phase 3 progress (tavern, pantry, and fall to Chult)

1. [x] Tavern doorway transition + common-room shell: bidirectional safe named
       arrivals, stable collision, readable sparse furniture, small wall stage,
       dedicated warm procedural tileset, and normal camera/audio behavior
       (sessions 54/58)
2. [x] Restrained tavern occupants, including the lanky green stage musician,
       plus barkeep cheese hook toward the pantry door, with the sole cheese on
       an impossible sky island and no inventory or progression state
       (sessions 55/58)
3. [x] Compact pantry room + normal/Astral/teal-sky floor language, connected
       safe route, storage dressing, and local Astral retry (session 56)
4. [x] Reused Astral fall death + distinct successful sky fall preserving
       Sanity and handing off to an input-free cutscene scene (session 57)
5. [x] Dedicated circa-1994 falling-to-Chult cutscene: deliberately long cloud
       descent, canopy collision, jungle impact, Astral return, cigarette drag,
       held non-playable Phase 4 handoff point, and a delayed high-intensity
       procedural action cue that resolves after impact (sessions 60-61)
