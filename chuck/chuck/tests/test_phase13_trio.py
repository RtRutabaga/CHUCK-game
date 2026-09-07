"""Phase 13's final trio encounter: the third time, and the worst.

Chuck has walked into the middle of these three twice before. The phase
document asks for this one to be the most chaotic version, and for the
chaos not to be paid for with readability -- it says so in as many
words: do not sacrifice gameplay readability simply to put more effects
on screen.

Those two pull against each other, so the map answers them separately
and both halves are tested. The floor is nine worlds jammed together
with no desert between them, and almost none of it is solid: chaotic in
material, clear in shape. What is dangerous is above the floor, and it
has edges a player can see.

The other thing worth pinning is what the wizard is doing. In the
sanctum and at the fortress he was shooting at something; here he is
working, and everything he throws goes east into the rift -- which is
the one direction Chuck can never be standing in, because there is
nothing past the heroes but Astral Sea. The biggest, loudest thing in
the room is by construction the one thing that cannot hurt him. That is
how a fight this crowded stays fair, and it is a property, so it is
measured rather than trusted.
"""

import json
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities.battle_actor import BattleActor
from src.entities.battle_hazards import (
    BattleChoreographer, CollisionBattleChoreographer,
    InfernalBattleChoreographer,
)
from src.scenes.dialogue_scene import DialogueScene
from src.systems.checkpoints import CHECKPOINT_BY_ID, DESERT_ENTRY_FLAGS
from src.world import collision
from src.world.tilemap import MARKER_DEFS, TileMap
from src.world.tileset_layout import COLLIDED, tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS

import sys
sys.path.insert(0, "tools")
from generate_desert_trio import (  # noqa: E402
    APPROACH, FIGHTER, GAP, GARRISON, HEIGHT, MID_Y, RANGER, RIM, WIDTH,
    WIZARD, patch_at,
)


MAP_NAME = "desert_trio"
BEHIND = "desert_east_8"

# The floors the arena is made of, and the worlds they came from.
FLOORS = {
    ".": "desert", "⌖": "desert ruin", "=": "modern city",
    "ᛗ": "chult", "ᛟ": "feywild", "·": "hell", "⌼": "ship",
    "⌽": "courtyard", "❄": "snow",
}


def _tilemap(name: str = MAP_NAME) -> TileMap:
    return TileMap(config.MAPS_DIR / f"{name}.txt")


def _world(checkpoint: str = MAP_NAME):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    world = game.checkpoints.load_checkpoint(
        checkpoint, progress_flags=set(DESERT_ENTRY_FLAGS)
    )
    world._arrival_fade_t = None
    return directory, game, world


def _safe_flood(tilemap: TileMap, origin) -> set[tuple[int, int]]:
    seen = {origin}
    frontier = [origin]
    while frontier:
        x, y = frontier.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            cell = (x + dx, y + dy)
            if cell in seen or tilemap.is_solid(*cell):
                continue
            if tilemap.terrain_at(*cell) in collision.FALL_HAZARD_TERRAIN:
                continue
            seen.add(cell)
            frontier.append(cell)
    return seen


def _reachable(tilemap: TileMap) -> set[tuple[int, int]]:
    ts = config.TILE_SIZE
    arrival = next(p for k, p in tilemap.object_spawns
                   if k == "arrival:from_east_8")
    return _safe_flood(tilemap, (int(arrival[0]) // ts, int(arrival[1]) // ts))


def test_the_floor_is_nine_worlds_and_almost_none_of_it_is_a_wall() -> None:
    """Chaotic in material, clear in shape -- both halves, separately.

    The document asks for this room to be the most chaotic version of
    an encounter the player has survived twice, and in the same breath
    says not to spend readability on spectacle. The way those two live
    together is that the chaos is underfoot and the danger is above it:
    every world Chuck has walked through is in the floor, and hardly
    anything in the room stops an arrow.
    """
    tilemap = _tilemap()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (WIDTH, HEIGHT)
    assert tileset_for(MAP_NAME) is COLLIDED

    inside = [
        (x, y) for y in range(RIM, HEIGHT - RIM)
        for x in range(RIM, WIDTH - RIM)
    ]
    floors = {patch_at(x, y) for x, y in inside}
    assert floors <= set(FLOORS), floors - set(FLOORS)
    assert len(floors) >= 8, sorted(floors)

    # ...and the patches are small. One world owning a quarter of the
    # arena is a region rather than a fragment, which is the thing this
    # room is specifically not.
    share: dict[str, int] = {}
    for x, y in inside:
        char = patch_at(x, y)
        share[char] = share.get(char, 0) + 1
    assert max(share.values()) / len(inside) < 0.25, {
        FLOORS[k]: round(v / len(inside), 3) for k, v in share.items()
    }

    # Hardly anything is solid. What is dangerous here is the stray
    # fire, and cover would turn a fight about movement into a fight
    # about hiding -- which is not a fight Chuck is allowed to win.
    solid = sum(1 for x, y in inside if tilemap.is_solid(x, y))
    assert solid / len(inside) < 0.02, solid


def test_the_three_of_them_are_the_same_three() -> None:
    """The established actors, not a third pair of sprites.

    A player has met these two times and is meant to recognise them on
    sight. Authoring new art for the last encounter would cost exactly
    that and nothing would fail, so the markers are checked against the
    battle-actor architecture the earlier two use.
    """
    tilemap = _tilemap()
    ts = config.TILE_SIZE
    placed = {
        kind: (int(p[0]) // ts, int(p[1]) // ts)
        for kind, p in tilemap.object_spawns if kind.startswith("battle:")
    }
    assert set(placed) == {"battle:fighter", "battle:wizard",
                           "battle:ranger"}, sorted(placed)
    assert placed["battle:fighter"] == FIGHTER
    assert placed["battle:wizard"] == WIZARD
    assert placed["battle:ranger"] == RANGER

    # Close enough together to be framed at once. The camera cuts to
    # them for their lines and lifts to clear the dialogue panel, so a
    # tableau spread down the map is a tableau you have to pan across.
    span = max(y for _, y in placed.values()) - min(
        y for _, y in placed.values())
    assert span * ts < config.NATIVE_HEIGHT - config.SANCTUM_ESTABLISH_LIFT, \
        span

    directory, game, world = _world()
    try:
        actors = {a.kind: a for a in world.battle_actors}
        assert set(actors) == {"fighter", "wizard", "ranger"}
        for actor in actors.values():
            assert isinstance(actor, BattleActor)
            assert actor._image is not None, actor.kind
        assert isinstance(world.battle, CollisionBattleChoreographer)
        # ...and it is a third choreography, not one of the first two.
        assert not isinstance(world.battle,
                              (BattleChoreographer,
                               InfernalBattleChoreographer))
    finally:
        game._shutdown()
        directory.cleanup()


def test_everything_the_wizard_throws_goes_where_chuck_cannot_be() -> None:
    """The rule that keeps the loudest thing in the room fair.

    He is working rather than fighting: every bolt goes east, into the
    rift. East of the heroes there is nothing but Astral Sea, so the
    biggest effect on screen is by construction the one thing that
    cannot reach the player -- and that is a property of the geometry
    rather than of the tuning, so it is checked against the map.
    """
    actors = [
        BattleActor(FIGHTER[0] * 16.0, FIGHTER[1] * 16.0, "fighter"),
        BattleActor(WIZARD[0] * 16.0, WIZARD[1] * 16.0, "wizard"),
        BattleActor(RANGER[0] * 16.0, RANGER[1] * 16.0, "ranger"),
    ]
    battle = CollisionBattleChoreographer(actors)

    bolts, arrows = [], []
    for _ in range(400):
        tick = battle.update(1 / 60)
        for shot in tick.projectiles:
            (bolts if shot.kind == "bolt" else arrows).append(shot)
    assert bolts and arrows, (len(bolts), len(arrows))

    # Every bolt goes east and nowhere else. Read off the velocity,
    # which is what the projectile keeps: the direction it was given is
    # normalised into vx/vy at construction.
    assert all(shot.vx > 0.0 for shot in bolts), "a bolt went inland"
    assert all(abs(shot.vy) < shot.vx for shot in bolts), "the fan is too wide"

    # ...and east of the wizard, on the map, there is no ground to
    # stand on: the bolts cross the rift and nothing else.
    tilemap = _tilemap()
    reachable = _reachable(tilemap)
    beyond = [
        (x, y) for (x, y) in reachable
        if x > WIZARD[0] and abs(y - WIZARD[1]) <= 6
    ]
    assert not beyond, beyond[:8]

    # The arrows are the opposite: they go everywhere, and that is the
    # hazard the room is actually made of.
    assert min(shot.vx for shot in arrows) < 0.0
    assert max(shot.vx for shot in arrows) > 0.0
    assert min(shot.vy for shot in arrows) < 0.0
    assert max(shot.vy for shot in arrows) > 0.0

    # Faster than the sanctum's, because this is the worst version of a
    # room he has survived twice. Compared, not asserted as a number.
    assert (CollisionBattleChoreographer.ARROW_INTERVAL
            < config.BATTLE_ARROW_INTERVAL)
    assert CollisionBattleChoreographer.ARROW_FAN > config.BATTLE_ARROW_FAN


def test_the_opening_lines_are_the_documents_and_play_on_arrival() -> None:
    """The words, and the moment they land.

    Same path as the other two encounters: the camera cuts to the three
    of them, the lines play, and control comes back. That sameness is
    most of what says these are the same people, so it is checked
    through the scene stack rather than by reading the JSON alone.
    """
    lines = json.loads(
        (config.DIALOGUE_DIR / "desert_trio.json").read_text(encoding="utf-8")
    )["trio_opening"]
    assert lines == [
        "There! It's opening!",
        "I see it. Hold them back!",
        "We've come too far to lose it now.",
    ], lines

    directory, game, world = _world()
    try:
        assert world._pending_entrance_dialogue == "trio_opening"
        world.update(1 / 60)
        scene = game.scenes.current
        assert isinstance(scene, DialogueScene), type(scene).__name__
        assert scene._lines == lines
        # The camera is on the tableau, not on the aisle he walked in by.
        cx, cy = world._battle_establishing_focus()
        assert abs(world.camera.x + config.NATIVE_WIDTH / 2 - cx) < 40, cx
        assert world._restore_camera_to_player
    finally:
        game._shutdown()
        directory.cleanup()


def test_most_of_the_adventure_is_pressing_them() -> None:
    """Familiar systems in a new combination, and nothing new at all.

    Six kinds of enemy, every one of them met somewhere behind this
    map, each standing on its own world's floor. What makes the room
    the culmination is not a new threat -- it is all of the old ones at
    once, in a place with nothing to hide behind.
    """
    tilemap = _tilemap()
    ts = config.TILE_SIZE
    kinds: dict[str, int] = {}
    for kind, position in tilemap.object_spawns:
        if kind.startswith(("arrival:", "anchor:", "battle:")):
            continue
        cell = (int(position[0]) // ts, int(position[1]) // ts)
        kinds[kind] = kinds.get(kind, 0) + 1
        expected = {
            ground for ground, marker, _ in GARRISON
            if MARKER_DEFS[marker].kind == kind
        }
        assert patch_at(*cell) in expected, (kind, cell, patch_at(*cell))
        # Never in the doorway: he walks into the middle of this and
        # should get to see it before it reaches him. The doorway is
        # the cleared strip at the west gap, not the whole west edge --
        # something standing in the far corner is scenery he can choose
        # to walk toward.
        in_doorway = (cell[0] <= RIM + APPROACH
                      and abs(cell[1] - MID_Y) <= GAP // 2 + 1)
        assert not in_doorway, (kind, cell)

    assert len(kinds) >= 5, sorted(kinds)
    for ground, marker, wanted in GARRISON:
        kind = MARKER_DEFS[marker].kind
        assert kinds.get(kind, 0) >= wanted, (kind, kinds.get(kind, 0))

    directory, game, world = _world()
    try:
        alive = (len(world.undead) + len(world.snakes) + len(world.redcaps)
                 + len(world.spined_devils))
        assert alive >= sum(count for _, _, count in GARRISON), alive
    finally:
        game._shutdown()
        directory.cleanup()


def test_he_can_reach_them_and_cannot_reach_the_rift() -> None:
    """Near enough to be in it, never near enough to help.

    The document is clear that Chuck survives this rather than
    resolving it. So the heroes are approachable -- the room would not
    read at all if they were on the far side of something -- and the
    thing they are working on is not.
    """
    tilemap = _tilemap()
    reachable = _reachable(tilemap)
    for name, (x, y) in (("fighter", FIGHTER), ("wizard", WIZARD),
                         ("ranger", RANGER)):
        assert any((x + dx, y + dy) in reachable
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))), name

    # The rift is most of the east and none of it can be stood on.
    rift = [
        (x, y) for y in range(RIM, HEIGHT - RIM)
        for x in range(WIDTH - 8, WIDTH - RIM)
        if tilemap.terrain_at(x, y) == "V"
    ]
    assert len(rift) > 200, len(rift)
    assert not set(rift) & reachable

    # ...and the only way off the map on his feet is the way in.
    edge = sorted(cell for cell in reachable
                  if cell[0] in (0, WIDTH - 1)
                  or cell[1] in (0, HEIGHT - 1))
    assert len(edge) == GAP, edge
    assert {cell[0] for cell in edge} == {0}


def test_the_walk_east_ends_here() -> None:
    assert AREA_WALK_EXITS[(BEHIND, "⮞")].destination == MAP_NAME
    assert AREA_WALK_EXITS[(MAP_NAME, "⮜")].destination == BEHIND
    # The one map east where the music changes. Every other map in
    # the phase shares the region's theme, which is what makes this
    # one landing as something else worth doing at all.
    assert AREA_MUSIC[MAP_NAME] != AREA_MUSIC[BEHIND]
    assert AREA_MUSIC[MAP_NAME] == "desert_trio.wav"

    ts = config.TILE_SIZE
    directory, game, world = _world(BEHIND)
    try:
        world.player.x = (world.tilemap.width_tiles - 1) * ts + 2
        world.player.y = (world.tilemap.height_tiles // 2) * ts + 2
        for _ in range(4):
            world.update(1 / 60)
        # Arriving pushes the heroes' opening lines straight on top of
        # the new map, so the scene on the stack under the conversation
        # is the one to look at.
        if isinstance(game.scenes.current, DialogueScene):
            game.scenes.pop()
        assert game.scenes.current.map_name == MAP_NAME
    finally:
        game._shutdown()
        directory.cleanup()

    # The phase document asks for the final encounter by name as a
    # development entry: it is the far end of a very long walk, and
    # testing it from the hub is not testing it.
    entry = CHECKPOINT_BY_ID[MAP_NAME]
    assert entry.display_name == "Final Trio Encounter"
    assert entry.development_visible and entry.runtime_entry
    assert entry.required_flags == DESERT_ENTRY_FLAGS
    assert CHECKPOINT_BY_ID[f"{MAP_NAME}_anchor"].saveable


def test_the_room_renders_with_all_three_in_the_shot() -> None:
    """Drawn, framed, and moving.

    The establishing shot is the thing this encounter is built around,
    so it is the thing that gets rendered: the camera where the lines
    put it, and all three of them inside the frame.
    """
    directory, game, world = _world()
    try:
        world._pending_entrance_dialogue = None
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        for _ in range(40):
            world.update(1 / 60)
        cx, cy = world._battle_establishing_focus()
        world.camera.focus_on(cx, cy)
        world.draw(surface)
        for actor in world.battle_actors:
            assert world.camera.y <= actor.y, actor.kind
            assert (actor.y + actor.height
                    <= world.camera.y + config.NATIVE_HEIGHT), actor.kind
        # ...and the room is live: the ranger has been throwing arrows
        # the whole time the camera was on them.
        assert world.battle_projectiles, "nothing is in the air"
    finally:
        game._shutdown()
        directory.cleanup()


def _run_all() -> None:
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  PASS  {name}")
            except AssertionError as exc:
                failures += 1
                print(f"  FAIL  {name}: {exc}")
    if failures:
        raise SystemExit(f"{failures} test(s) failed")
    print("All trio encounter tests passed.")


if __name__ == "__main__":
    _run_all()
