"""Phase 7 staged starboard plank and ordered approach."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities.deck_pirate import DeckPirateNPC
from src.entities.reality_blocks import (
    HELL_BASALT_COLORS,
    HELL_LAVA_COLORS,
    RealityBlockField,
)
from src.scenes.dialogue_scene import DialogueScene
from src.scenes.hell_falling_cutscene_scene import (
    HELL_ARRIVAL_TIME,
    HELL_CIGARETTE_SEATED,
    HELL_CIGARETTE_START,
    HELL_GROUND_APPROACH,
    HELL_IMPACT_TIME,
    HELL_LOOK_START,
    HELL_MUSIC_START,
    HellFallingCutsceneScene,
)
from src.systems.captain_confrontation import (
    CAPTAIN_CONFRONTED_FLAG,
    CAPTAIN_REQUIRED_FLAGS,
    DECK_PLANK_LENGTH,
    DECK_PLANK_TERRAIN,
    DECK_PLANK_WIDTH,
)
from src.systems.ship_motion import deck_rock_offset
from src.world.tilemap import TileMap
from src.world.tileset_layout import SEWER, TILE_PX, tileset_for


MAP_NAME = "ship_exterior_deck"
PLANK_ORIGIN = (42, 32)


def _pirate(scene, npc_id: str) -> DeckPirateNPC:
    return next(
        npc for npc in scene.npcs
        if isinstance(npc, DeckPirateNPC) and npc.npc_id == npc_id
    )


def _tile_centered_position(entity, col: int, row: int) -> tuple[float, float]:
    ts = config.TILE_SIZE
    return (
        col * ts + (ts - entity.width) / 2,
        row * ts + (ts - entity.height) / 2,
    )


def _plank_centered_position(entity, row: int) -> tuple[float, float]:
    ts = config.TILE_SIZE
    first_col, _first_row = PLANK_ORIGIN
    return (
        (first_col + DECK_PLANK_WIDTH / 2) * ts - entity.width / 2,
        row * ts + (ts - entity.height) / 2,
    )


def test_map_authors_one_plank_origin_in_the_starboard_rail() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    origins = [
        position for kind, position in tilemap.object_spawns
        if kind == "deck_plank_origin"
    ]
    assert origins == [(
        PLANK_ORIGIN[0] * config.TILE_SIZE + 8,
        PLANK_ORIGIN[1] * config.TILE_SIZE + 8,
    )]
    assert tilemap.terrain_at(*PLANK_ORIGIN) == "═"
    assert tilemap.is_solid(*PLANK_ORIGIN)
    assert tileset_for(MAP_NAME).char_to_terrain[DECK_PLANK_TERRAIN] == (
        "ship_plank"
    )


def test_plank_is_hidden_before_confrontation_and_staged_afterward() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint(MAP_NAME)
        first_col, first_row = PLANK_ORIGIN
        assert all(
            scene.tilemap.terrain_at(col, first_row) == "═"
            for col in range(first_col, first_col + DECK_PLANK_WIDTH)
        )
        assert all(
            scene.tilemap.terrain_at(col, row) != DECK_PLANK_TERRAIN
            for col in range(first_col, first_col + DECK_PLANK_WIDTH)
            for row in range(first_row, first_row + DECK_PLANK_LENGTH)
        )

        scene = game.checkpoints.load_checkpoint(
            MAP_NAME,
            progress_flags=(
                CAPTAIN_REQUIRED_FLAGS | {CAPTAIN_CONFRONTED_FLAG}
            ),
        )
        assert all(
            scene.tilemap.terrain_at(col, row) == DECK_PLANK_TERRAIN
            and not scene.tilemap.is_solid(col, row)
            for col in range(first_col, first_col + DECK_PLANK_WIDTH)
            for row in range(first_row, first_row + DECK_PLANK_LENGTH)
        )
        assert all(
            scene.tilemap.terrain_at(
                col, first_row + DECK_PLANK_LENGTH
            ) == "~"
            and scene.tilemap.is_solid(
                col, first_row + DECK_PLANK_LENGTH
            )
            for col in range(first_col, first_col + DECK_PLANK_WIDTH)
        )
        assert scene.tilemap.is_solid(first_col - 1, first_row + 2)
        assert scene.tilemap.is_solid(
            first_col + DECK_PLANK_WIDTH, first_row + 2
        )
    finally:
        game._shutdown()


def test_completed_state_places_captain_and_objector_at_the_approach() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint(
            MAP_NAME,
            progress_flags=(
                CAPTAIN_REQUIRED_FLAGS | {CAPTAIN_CONFRONTED_FLAG}
            ),
        )
        captain = _pirate(scene, "captain_pirate")
        objector = _pirate(scene, "cheering_pirate")
        assert (captain.x, captain.y) == _tile_centered_position(
            captain, 39, 30
        )
        assert (objector.x, objector.y) == _tile_centered_position(
            objector, 46, 30
        )
        assert captain.facing == "right"
        assert objector.facing == "left"
        assert not scene._plank_procession_active
    finally:
        game._shutdown()


def test_dialogue_hands_off_to_short_scripted_walk_then_returns_control() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint(
            MAP_NAME, progress_flags=CAPTAIN_REQUIRED_FLAGS
        )
        scene.update(0.0)
        assert scene._captain_arrival_active
        for _ in range(100):
            scene.update(0.1)
            if isinstance(game.scenes.current, DialogueScene):
                break
        assert isinstance(game.scenes.current, DialogueScene)
        assert game.scenes.current._lines == ["Captain on deck!", "..."]
        game.scenes.pop()

        scene.update(0.0)
        assert isinstance(game.scenes.current, DialogueScene)
        game.scenes.pop()

        scene.update(0.0)
        assert scene._plank_procession_active
        assert game.progress.has(CAPTAIN_CONFRONTED_FLAG)
        assert (scene.player.x, scene.player.y) == _plank_centered_position(
            scene.player, 27
        )
        assert scene.player.facing == "down"
        assert all(
            scene.tilemap.terrain_at(col, row) == DECK_PLANK_TERRAIN
            for col in range(42, 42 + DECK_PLANK_WIDTH)
            for row in range(32, 32 + DECK_PLANK_LENGTH)
        )

        scene.update(2.0)
        assert not scene._plank_procession_active
        assert scene._plank_procession_target is None
        assert (scene.player.x, scene.player.y) == _plank_centered_position(
            scene.player, 31
        )
        assert not scene.player.moving
        assert game.scenes.current is scene
    finally:
        game._shutdown()


def test_reality_field_streams_both_materials_east_to_west_and_recycles() -> None:
    field = RealityBlockField(*PLANK_ORIGIN)
    assert not field.active and not field.visible_blocks
    field.activate()
    assert len(field.visible_blocks) == 1
    first = field.visible_blocks[0]
    east_x, lane_y = field.position(first)
    assert east_x == field.east_x(first)
    assert east_x >= config.NATIVE_WIDTH - 8

    field.update(0.5)
    moved_x, moved_y = field.position(first)
    assert moved_x < east_x
    assert moved_y == lane_y

    field.update(2.0)
    assert {block.kind for block in field.visible_blocks} == {"astral", "hell"}

    # Just before a complete crossing ends, the first block is entirely west
    # of the screen. The next update wraps a replacement to the east edge.
    field.age = (
        first.delay + field.travel_distance(first) / first.speed - 0.05
    )
    west_x, _ = field.position(first)
    assert west_x + first.width < 0
    field.update(0.1)
    recycled_x, _ = field.position(first)
    assert recycled_x > config.NATIVE_WIDTH - 20


def test_reality_field_reuses_exact_animated_astral_fall_tiles() -> None:
    game = Game()
    try:
        field = RealityBlockField(*PLANK_ORIGIN)
        field.load_art(game.assets)
        assert len(field._astral_frames) == 6

        image = pygame.Surface((3 * TILE_PX, 2 * TILE_PX), pygame.SRCALPHA)
        field._draw_astral(image, seed=0)
        sheet_rows = game.assets.tileset(SEWER.sheet, TILE_PX)
        astral_row = next(
            index
            for index, (name, _variants, _frames) in enumerate(SEWER.order)
            if name == "astral_void"
        )
        expected = sheet_rows[astral_row]
        first_tile = image.subsurface((0, 0, TILE_PX, TILE_PX))
        second_tile = image.subsurface((TILE_PX, 0, TILE_PX, TILE_PX))
        assert pygame.image.tobytes(first_tile, "RGBA") == (
            pygame.image.tobytes(expected[0], "RGBA")
        )
        assert pygame.image.tobytes(second_tile, "RGBA") == (
            pygame.image.tobytes(expected[3], "RGBA")
        )
    finally:
        game._shutdown()


def test_hell_blocks_read_as_overhead_basalt_terrain_and_lava() -> None:
    field = RealityBlockField(*PLANK_ORIGIN)
    field.activate()
    field.update(0.75)
    image = pygame.Surface((3 * TILE_PX, 2 * TILE_PX), pygame.SRCALPHA)
    field._draw_hell(image, image.get_rect(), seed=3)

    pixels = [
        image.get_at((x, y))[:3]
        for y in range(image.get_height())
        for x in range(image.get_width())
    ]
    basalt = sum(pixel in HELL_BASALT_COLORS for pixel in pixels)
    lava = sum(pixel in HELL_LAVA_COLORS for pixel in pixels)
    assert basalt > len(pixels) * 0.45
    assert lava > len(pixels) * 0.12
    assert HELL_LAVA_COLORS[-1] in pixels

    # There is no longer a side-facing flame strip along the top edge: both
    # basalt plate tops and exposed lava channels meet the fragment boundary.
    top_edge = {
        image.get_at((x, 1))[:3] for x in range(1, image.get_width() - 1)
    }
    assert top_edge & set(HELL_BASALT_COLORS)
    assert top_edge & set(HELL_LAVA_COLORS)


def test_hell_fragments_use_distinct_nonuniform_lava_layouts() -> None:
    field = RealityBlockField(*PLANK_ORIGIN)
    images = []
    for seed in (1, 3):
        image = pygame.Surface((3 * TILE_PX, 3 * TILE_PX), pygame.SRCALPHA)
        field._draw_hell(image, image.get_rect(), seed)
        images.append(image)

    first, second = images
    first_bytes = pygame.image.tobytes(first, "RGBA")
    second_bytes = pygame.image.tobytes(second, "RGBA")
    assert first_bytes != second_bytes

    # Lava openings should not repeat at fixed 12-pixel grid intersections
    # across separately seeded fragments.
    first_lava = {
        (x, y)
        for y in range(first.get_height())
        for x in range(first.get_width())
        if first.get_at((x, y))[:3] in HELL_LAVA_COLORS
    }
    second_lava = {
        (x, y)
        for y in range(second.get_height())
        for x in range(second.get_width())
        if second.get_at((x, y))[:3] in HELL_LAVA_COLORS
    }
    overlap = len(first_lava & second_lava)
    assert overlap < min(len(first_lava), len(second_lava)) * 0.65


def test_stepping_onto_plank_reveals_blocks_and_triggers_jeffries_once() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint(
            MAP_NAME,
            progress_flags=(
                CAPTAIN_REQUIRED_FLAGS | {CAPTAIN_CONFRONTED_FLAG}
            ),
        )
        assert scene.reality_blocks is not None
        assert not scene.reality_blocks.active
        assert scene.dialogue.get("jeffries_reality_warning") == [
            "It's back! The purple is back!"
        ]

        scene.player.x, scene.player.y = _tile_centered_position(
            scene.player, PLANK_ORIGIN[0] + DECK_PLANK_WIDTH - 1,
            PLANK_ORIGIN[1],
        )
        scene.update(0.0)
        warning = game.scenes.current
        assert isinstance(warning, DialogueScene)
        assert warning._lines == ["It's back! The purple is back!"]
        assert scene.reality_blocks.active
        assert scene._reality_warning_shown
        assert scene._fall_t is None
        assert scene._pending_map is None

        # The plank stays walkable and its solid ocean endpoint still prevents
        # ordinary movement from leaving it. The ending owns that departure.
        first_col, first_row = PLANK_ORIGIN
        assert all(
            scene.tilemap.terrain_at(col, row) == DECK_PLANK_TERRAIN
            for col in range(first_col, first_col + DECK_PLANK_WIDTH)
            for row in range(first_row, first_row + DECK_PLANK_LENGTH)
        )
        assert all(
            scene.tilemap.is_solid(
                col, first_row + DECK_PLANK_LENGTH
            )
            for col in range(first_col, first_col + DECK_PLANK_WIDTH)
        )
        game.scenes.pop()
        before = [
            scene.reality_blocks.position(block)
            for block in scene.reality_blocks.visible_blocks
        ]
        scene.update(1.0)
        after = [
            scene.reality_blocks.position(block)
            for block in scene.reality_blocks.visible_blocks[:len(before)]
        ]
        assert before != after
        assert game.scenes.current is scene
        assert scene._fall_t is None and scene._pending_map is None

        # Remaining near the approach does not repeat Jeffries' line or start
        # the kick before Chuck commits to the outer tile.
        scene.update(0.0)
        assert game.scenes.current is scene
        assert scene._plank_ending_phase is None
    finally:
        game._shutdown()


def test_outer_plank_stages_captain_kick_into_a_live_hell_fragment() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint(
            MAP_NAME,
            progress_flags=(
                CAPTAIN_REQUIRED_FLAGS | {CAPTAIN_CONFRONTED_FLAG}
            ),
        )
        assert scene.reality_blocks is not None
        scene.reality_blocks.activate()
        scene._reality_warning_shown = True
        sounds = []
        game.audio.play_sfx = sounds.append

        first_col, first_row = PLANK_ORIGIN
        last_row = first_row + DECK_PLANK_LENGTH - 1
        scene.player.x, scene.player.y = _tile_centered_position(
            scene.player, first_col, last_row
        )
        scene.camera.follow(scene.player)
        scene.camera.update(0.0)
        scene.update(0.0)
        assert scene._plank_ending_phase == "approach"
        assert scene.player.facing == "down"
        assert scene.player.x == _plank_centered_position(
            scene.player, last_row
        )[0]

        saw_kick = False
        saw_fall = False
        for _ in range(180):
            scene.update(0.1)
            captain = _pirate(scene, "captain_pirate")
            saw_kick = saw_kick or captain.kick_progress is not None
            saw_fall = saw_fall or scene.player.fall_progress is not None
            if game.scenes.current is not scene:
                break

        cutscene = game.scenes.current
        assert isinstance(cutscene, HellFallingCutsceneScene)
        assert scene._plank_ending_block.kind == "hell"
        assert saw_kick and saw_fall
        assert sounds == ["hurt"]
        assert cutscene.sanity == scene.sanity.current
        block_x, block_y = scene.reality_blocks.position(
            scene._plank_ending_block
        )
        rock_x, rock_y = deck_rock_offset(scene._world_time)
        player_screen_center = (
            scene.player.x + scene.player.width / 2
            - round(scene.camera.x) + rock_x,
            scene.player.y + scene.player.height / 2
            - round(scene.camera.y) + rock_y,
        )
        assert block_x <= player_screen_center[0] <= (
            block_x + scene._plank_ending_block.width
        )
        assert block_y <= player_screen_center[1] <= (
            block_y + scene._plank_ending_block.height
        )
    finally:
        game._shutdown()


def test_hell_fall_reuses_cue_and_holds_at_phase8_arrival_boundary() -> None:
    game = Game()
    try:
        scene = HellFallingCutsceneScene(game, sanity=73)
        game.scenes.replace(scene)
        music = []
        sounds = []
        game.audio.play_music = lambda filename, loop=True: music.append(
            (filename, loop)
        )
        game.audio.play_sfx = sounds.append
        assert not hasattr(scene, "fragments")

        scene.update(HELL_MUSIC_START - 0.1)
        assert music == []
        scene.update(0.2)
        assert music == [("fall_to_chult.wav", False)]

        def _volcano_pixels(rows=None):
            frame = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
            scene.draw(frame)
            ys = rows if rows is not None else range(config.NATIVE_HEIGHT)
            count = 0
            colours = set()
            for y in ys:
                for x in range(config.NATIVE_WIDTH):
                    px = frame.get_at((x, y))[:3]
                    colours.add(px)
                    if px == (34, 23, 25):
                        count += 1
            return count, colours

        # Early in the fall the volcano is still below the frame — empty
        # heated air, no landmark yet, and certainly no ground.
        early, early_colours = _volcano_pixels()
        assert early < 100, early
        assert not set(HELL_BASALT_COLORS) & early_colours

        # By the time the ground nears, the volcano has climbed fully into
        # view (its silhouette fills the lower frame) and reaches flush to
        # the bottom of the picture.
        scene.update(HELL_GROUND_APPROACH - scene.elapsed - 0.01)
        assert scene.phase == "fall"
        full, _ = _volcano_pixels()
        assert full > 1000, full
        bottom, _ = _volcano_pixels(rows=range(160, 173))
        assert bottom > 0, "the volcano should reach the bottom, no gap"

        scene.update(0.02)
        assert scene.phase == "approach"
        game.scenes.draw(game.native_surface)

        scene.update(HELL_IMPACT_TIME - scene.elapsed + 0.01)
        assert scene.phase == "impact"
        assert sounds == ["hurt"]
        game.scenes.draw(game.native_surface)

        scene.update(HELL_LOOK_START - scene.elapsed + 0.01)
        assert scene.phase == "look"
        assert scene._facing_for_tableau() == "left"
        scene.update(0.75)
        assert scene._facing_for_tableau() == "right"
        scene.update(HELL_CIGARETTE_START - scene.elapsed + 0.01)
        assert scene.phase == "cigarette"
        assert not scene.cigarette_lit
        scene.update(HELL_CIGARETTE_SEATED - scene.elapsed + 0.01)
        assert scene.phase == "smoke"
        assert scene.cigarette_lit

        ground = pygame.Surface((config.NATIVE_WIDTH, 48))
        scene._draw_basalt_ground(ground)
        ground_pixels = [
            ground.get_at((x, y))[:3]
            for y in range(ground.get_height())
            for x in range(ground.get_width())
        ]
        basalt = sum(pixel in HELL_BASALT_COLORS for pixel in ground_pixels)
        lava = sum(pixel in HELL_LAVA_COLORS for pixel in ground_pixels)
        assert basalt > len(ground_pixels) * 0.9
        assert lava < len(ground_pixels) * 0.02

        scene.update(HELL_ARRIVAL_TIME - scene.elapsed + 1.0)
        assert scene.arrived and scene.phase == "arrived"
        assert scene.elapsed == HELL_ARRIVAL_TIME
        assert scene.sanity == 73
        assert game.scenes.current is scene
        held_elapsed = scene.elapsed
        scene.update(5.0)
        assert scene.elapsed == held_elapsed
        game.scenes.draw(game.native_surface)
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
    print("All Phase 7 plank-procession tests passed.")


if __name__ == "__main__":
    _run_all()
