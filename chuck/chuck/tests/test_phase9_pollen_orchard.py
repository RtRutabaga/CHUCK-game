"""Phase 9's Pollen Orchard and immediate slowing-terrain behavior."""

from collections import Counter, deque
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities.player import Player
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.systems.reactive_flowers import ReactiveFlowerController
from src.systems.terrain_effect import ground_speed_multiplier
from src.world.tilemap import TileMap
from src.world.tileset_layout import MAP_TILESET
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


MAP_NAME = "feywild_pollen_orchard"


class FakeInput:
    def __init__(self) -> None:
        self.press_jump = False

    def was_pressed(self, action: str) -> bool:
        pressed = action == "jump" and self.press_jump
        self.press_jump = False
        return pressed

    def movement_vector(self) -> tuple[float, float]:
        return (0.0, 0.0)


def _marker_positions(tilemap: TileMap, prefix: str = ""):
    size = config.TILE_SIZE
    return [
        (kind, (int(x // size), int(y // size)))
        for kind, (x, y) in tilemap.object_spawns
        if kind.startswith(prefix)
    ]


def _reachable(tilemap: TileMap, start: tuple[int, int]):
    reached = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for point in (
            (col - 1, row), (col + 1, row),
            (col, row - 1), (col, row + 1),
        ):
            if point in reached or tilemap.is_solid(*point):
                continue
            reached.add(point)
            frontier.append(point)
    return reached


def test_orchard_is_a_large_enemy_free_pollen_lesson() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    assert (tilemap.width_tiles, tilemap.height_tiles) == (62, 46)
    assert MAP_TILESET[MAP_NAME] == "feywild"
    assert AREA_MUSIC[MAP_NAME] == "feywild.wav"
    assert AREA_MUSIC[MAP_NAME] == AREA_MUSIC["feywild_blooming_path"]
    assert AREA_MUSIC[MAP_NAME] == AREA_MUSIC["feywild_riverbank"]

    kinds = Counter(kind for kind, _position in tilemap.object_spawns)
    assert kinds["arrival:from_feywild_2"] == 1
    assert kinds["anchor:feywild_3_anchor"] == 1
    assert kinds["boundary:feywild_4"] == 1
    assert kinds["arrival:from_feywild_4"] == 1
    assert kinds["flower_switch:orchard"] == 1
    assert kinds["flower_open:orchard"] == 3
    assert kinds["flower_close:orchard"] == 3
    assert kinds["breakable_grass"] == 1
    assert not any(
        kind in {
            "rat", "snake", "zombie", "skeleton", "lemure", "raptor",
            "massive_dinosaur", "horned_devil", "fire_snake",
        }
        for kind in kinds
    )
    assert sum(
        tilemap.terrain_at(col, row) == "\u263c"
        for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
    ) == 15


def test_both_orchard_flower_routes_reach_every_required_landmark() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers = dict(_marker_positions(tilemap))
    controller = ReactiveFlowerController(tilemap, tilemap.object_spawns)
    arrival = markers["arrival:from_feywild_2"]
    required = {
        markers["anchor:feywild_3_anchor"],
        markers["boundary:feywild_4"],
        markers["arrival:from_feywild_4"],
        markers["flower_switch:orchard"],
    }
    assert required <= _reachable(tilemap, arrival)

    assert controller.trigger("orchard")
    controller.update(
        config.REACTIVE_FLOWER_CHANGE_DELAY,
        pygame.Rect(-100, -100, 1, 1),
    )
    assert controller.groups["orchard"].active
    assert required <= _reachable(tilemap, arrival)


def test_pollen_multiplier_is_grounded_immediate_and_non_stacking() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    pollen = next(
        (col, row)
        for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
        if tilemap.terrain_at(col, row) == "\u263c"
    )
    size = config.TILE_SIZE
    on_pollen = pygame.Rect(
        pollen[0] * size + 3, pollen[1] * size + 4,
        config.PLAYER_HITBOX_W, config.PLAYER_HITBOX_H,
    )
    on_path = pygame.Rect(8 * size, 43 * size, 8, 8)

    assert ground_speed_multiplier(
        tilemap, on_pollen, airborne=False
    ) == config.FEYWILD_POLLEN_SPEED_MULTIPLIER
    assert ground_speed_multiplier(tilemap, on_pollen, airborne=True) == 1.0
    assert ground_speed_multiplier(tilemap, on_path, airborne=False) == 1.0


def test_world_contact_slows_walking_without_sanity_damage() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("feywild_3", sanity=67)
        pollen = next(
            (col, row)
            for row in range(scene.tilemap.height_tiles)
            for col in range(scene.tilemap.width_tiles)
            if scene.tilemap.terrain_at(col, row) == "\u263c"
        )
        scene.player.x = pollen[0] * config.TILE_SIZE + 3
        scene.player.y = pollen[1] * config.TILE_SIZE + 4
        start_x = scene.player.x
        game.input._actions_down.add("move_right")
        scene.update(0.1)

        expected = (
            config.PLAYER_SPEED
            * config.FEYWILD_POLLEN_SPEED_MULTIPLIER
            * 0.1
        )
        assert abs(scene.player.x - start_x - expected) < 0.01
        assert scene.sanity.current == 67

        game.input._actions_down.clear()
        scene.player.x = 8 * config.TILE_SIZE
        scene.player.y = 43 * config.TILE_SIZE
        scene.update(0.0)
        assert scene.player.ground_speed_multiplier == 1.0
    finally:
        game._shutdown()


def test_committed_jump_clears_the_one_tile_intro_strip() -> None:
    controls = FakeInput()
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    player = Player(
        15 * config.TILE_SIZE + 3,
        38 * config.TILE_SIZE + 4,
        controls,
    )
    player.tilemap = tilemap
    player.facing = "up"
    controls.press_jump = True
    for _ in range(12):
        player.update(0.03)
    assert not player.jumping
    assert (player.y + player.height / 2) // config.TILE_SIZE <= 36


def test_orchard_uses_shared_transitions_checkpoints_and_save() -> None:
    forward = AREA_WALK_EXITS[("feywild_blooming_path", "\u2192")]
    backward = AREA_WALK_EXITS[(MAP_NAME, "\u21e9")]
    assert forward.destination == MAP_NAME
    assert forward.arrival == "from_feywild_2"
    assert backward.destination == "feywild_blooming_path"
    assert backward.arrival == "from_feywild_3"

    entry = CHECKPOINT_BY_ID["feywild_3"]
    anchor = CHECKPOINT_BY_ID["feywild_3_anchor"]
    return_entry = CHECKPOINT_BY_ID["feywild_2_return"]
    assert entry.display_name == "Feywild 3" and entry.runtime_entry
    assert anchor.map_name == MAP_NAME and anchor.saveable
    assert not anchor.development_visible
    assert return_entry.arrival == "from_feywild_3"

    with tempfile.TemporaryDirectory() as directory:
        game = Game(save_path=Path(directory) / "save.json")
        try:
            scene = game.checkpoints.load_checkpoint("feywild_3", sanity=59)
            assert scene.map_name == MAP_NAME
            assert scene.undead == [] and scene.raptors == []
            ashtray = scene.anchors[0]
            scene.player.x = ashtray.x
            scene.player.y = ashtray.y
            scene.update(0.0)
            assert ashtray.lit
            assert game.active_checkpoint_id == "feywild_3_anchor"

            resumed = game.checkpoints.continue_game()
            assert resumed is not None
            assert resumed.map_name == MAP_NAME
            assert resumed.sanity.current == 59
            assert resumed.anchors[0].lit
            assert not resumed.reactive_flowers.groups["orchard"].active
        finally:
            game._shutdown()


def test_blooming_path_and_orchard_transition_both_ways() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("feywild_2")
        forward_tile = next(
            (col, row)
            for row, terrain_row in enumerate(scene.tilemap._grid)
            for col, char in enumerate(terrain_row)
            if char == "\u2192"
        )
        scene.player.x = forward_tile[0] * config.TILE_SIZE + 3
        scene.player.y = forward_tile[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == MAP_NAME
        assert game.active_checkpoint_id == "feywild_3"

        return_tile = next(
            (col, row)
            for row, terrain_row in enumerate(scene.tilemap._grid)
            for col, char in enumerate(terrain_row)
            if char == "\u21e9"
        )
        scene.player.x = return_tile[0] * config.TILE_SIZE + 3
        scene.player.y = return_tile[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == "feywild_blooming_path"
        assert game.active_checkpoint_id == "feywild_2_return"
    finally:
        game._shutdown()


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
    print("All Phase 9 Pollen Orchard tests passed.")


if __name__ == "__main__":
    _run_all()
