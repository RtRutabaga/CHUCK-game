"""Authored checkpoints and the one shared checkpoint-loading path.

NEW GAME, CONTINUE, and the temporary development selector all choose an ID
from this registry and call CheckpointLoader.load_checkpoint(). Map transitions
also use registry entries to preserve the established local-respawn behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from src.core import config
from src.systems.save import SaveRecord, SaveSystem

if TYPE_CHECKING:
    from src.core.game import Game


KNOWN_PROGRESS_FLAGS = frozenset({"sewer_completed", "chult_reached"})
OPENING_CHECKPOINT_ID = "waterdeep_start"


@dataclass(frozen=True)
class CheckpointDefinition:
    checkpoint_id: str
    display_name: str
    map_name: str
    position: tuple[float, float] | None = None
    arrival: str | None = None
    facing: str | None = None
    climb_from_water: bool = False
    required_flags: frozenset[str] = field(default_factory=frozenset)
    saveable: bool = False
    development_visible: bool = True
    runtime_entry: bool = False
    fade_in: bool = False


CHECKPOINTS = (
    CheckpointDefinition(
        "waterdeep_start", "Waterdeep 1", "waterdeep_docks",
        facing="down", runtime_entry=True,
    ),
    CheckpointDefinition(
        "waterdeep_anchor", "Waterdeep Ashtray", "waterdeep_docks",
        position=(372.0, 421.0), facing="down", saveable=True,
    ),
    CheckpointDefinition(
        "sewer_entrance", "Sewer 1", "sewer",
        facing="down", runtime_entry=True,
    ),
    CheckpointDefinition(
        "sewer_anchor", "Sewer 2", "sewer",
        position=(196.0, 917.0), facing="down", saveable=True,
    ),
    CheckpointDefinition(
        "waterdeep_return", "Waterdeep 2", "waterdeep_docks",
        arrival="sewer_outflow", facing="up", climb_from_water=True,
        required_flags=frozenset({"sewer_completed"}), runtime_entry=True,
    ),
    CheckpointDefinition(
        "tavern_entry", "Tavern 1", "waterdeep_tavern",
        arrival="front_entrance", facing="up",
        required_flags=frozenset({"sewer_completed"}), runtime_entry=True,
    ),
    CheckpointDefinition(
        "pantry_entry", "Pantry 1", "waterdeep_pantry",
        arrival="pantry_entry", facing="up",
        required_flags=frozenset({"sewer_completed"}), runtime_entry=True,
    ),
    CheckpointDefinition(
        "chult_anchor", "Chult 1", "chult_jungle",
        position=(500.0, 837.0), facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        saveable=True,
    ),
    CheckpointDefinition(
        "chult_landing", "Chult Landing", "chult_jungle",
        facing="down",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        development_visible=False, runtime_entry=True, fade_in=True,
    ),
    CheckpointDefinition(
        "chult_2", "Chult 2", "chult_cog",
        arrival="from_chult_1", facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "chult_2_anchor", "Chult 2 Ashtray", "chult_cog",
        position=(644.0, 1157.0), facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        saveable=True, development_visible=False,
    ),
    # Internal return entries keep existing local retry positions, but do not
    # clutter the temporary test menu.
    CheckpointDefinition(
        "waterdeep_tavern_return", "Waterdeep Tavern Return",
        "waterdeep_docks", arrival="tavern_return", facing="down",
        required_flags=frozenset({"sewer_completed"}),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "tavern_pantry_return", "Tavern Pantry Return",
        "waterdeep_tavern", arrival="pantry_return", facing="down",
        required_flags=frozenset({"sewer_completed"}),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "tavern_default", "Tavern Default Spawn", "waterdeep_tavern",
        required_flags=frozenset({"sewer_completed"}),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "pantry_default", "Pantry Default Spawn", "waterdeep_pantry",
        required_flags=frozenset({"sewer_completed"}),
        development_visible=False, runtime_entry=True,
    ),
)

CHECKPOINT_BY_ID = {checkpoint.checkpoint_id: checkpoint for checkpoint in CHECKPOINTS}


class ProgressState:
    """The deliberately tiny set of durable world-state flags."""

    def __init__(self) -> None:
        self.flags: set[str] = set()

    def replace(self, flags) -> None:
        flags = set(flags)
        unknown = flags - KNOWN_PROGRESS_FLAGS
        if unknown:
            raise ValueError(f"Unknown progress flags: {sorted(unknown)}")
        self.flags = flags

    def enable(self, flag: str) -> None:
        if flag not in KNOWN_PROGRESS_FLAGS:
            raise ValueError(f"Unknown progress flag {flag!r}")
        self.flags.add(flag)

    def has(self, flag: str) -> bool:
        return flag in self.flags


class CheckpointLoader:
    """Owns checkpoint selection, initialization, and save restoration."""

    def __init__(self, game: "Game", saves: SaveSystem) -> None:
        self.game = game
        self.saves = saves

    @property
    def development_checkpoints(self) -> tuple[CheckpointDefinition, ...]:
        return tuple(cp for cp in CHECKPOINTS if cp.development_visible)

    def definition(self, checkpoint_id: str) -> CheckpointDefinition:
        try:
            return CHECKPOINT_BY_ID[checkpoint_id]
        except KeyError as exc:
            raise KeyError(f"Unknown checkpoint {checkpoint_id!r}") from exc

    def entry_checkpoint_id(self, map_name: str, arrival: str | None) -> str:
        matches = [
            cp.checkpoint_id for cp in CHECKPOINTS
            if cp.runtime_entry and cp.map_name == map_name and cp.arrival == arrival
        ]
        if len(matches) != 1:
            raise ValueError(
                f"Expected one runtime checkpoint for {map_name!r} arrival "
                f"{arrival!r}, found {matches}"
            )
        return matches[0]

    def set_runtime_checkpoint(self, checkpoint_id: str) -> None:
        """Set the local retry point without writing the player save slot."""
        checkpoint = self.definition(checkpoint_id)
        self.game.progress.flags.update(checkpoint.required_flags)
        self.game.active_checkpoint_id = checkpoint_id

    def load_checkpoint(
        self,
        checkpoint_id: str,
        *,
        progress_flags=None,
        sanity: int | None = None,
    ):
        """Rebuild a checkpoint identically for NEW, CONTINUE, or development."""
        from src.scenes.world_scene import WorldScene

        checkpoint = self.definition(checkpoint_id)
        flags = set(checkpoint.required_flags)
        if progress_flags is not None:
            flags.update(progress_flags)
        self.game.progress.replace(flags)
        self.game.active_checkpoint_id = checkpoint_id
        scene = WorldScene(
            self.game,
            checkpoint.map_name,
            initial_arrival=checkpoint.arrival,
            initial_position=checkpoint.position,
            initial_facing=checkpoint.facing,
            initial_climb_from_water=checkpoint.climb_from_water,
            initial_sanity=(config.SANITY_START if sanity is None else sanity),
            initial_checkpoint_id=checkpoint_id,
            initial_fade_in=checkpoint.fade_in,
        )
        self.game.scenes.replace(scene)
        return scene

    def new_game(self):
        self.saves.delete()
        return self.load_checkpoint(OPENING_CHECKPOINT_ID)

    def valid_save(self) -> SaveRecord | None:
        record = self.saves.load()
        if record is None:
            return None
        checkpoint = CHECKPOINT_BY_ID.get(record.checkpoint_id)
        if checkpoint is None or not checkpoint.saveable:
            return None
        if not set(record.progress_flags) <= KNOWN_PROGRESS_FLAGS:
            return None
        return record

    @property
    def can_continue(self) -> bool:
        return self.valid_save() is not None

    def continue_game(self):
        record = self.valid_save()
        if record is None:
            return None
        return self.load_checkpoint(
            record.checkpoint_id,
            progress_flags=record.progress_flags,
            sanity=record.sanity,
        )

    def activate_checkpoint(self, checkpoint_id: str, sanity: int) -> bool:
        """Attune an authored Anchor and persist only durable resume state."""
        checkpoint = self.definition(checkpoint_id)
        if not checkpoint.saveable:
            raise ValueError(f"Checkpoint {checkpoint_id!r} is not an Ashtray")
        self.set_runtime_checkpoint(checkpoint_id)
        record = SaveRecord(
            checkpoint_id=checkpoint_id,
            sanity=sanity,
            progress_flags=tuple(sorted(self.game.progress.flags)),
        )
        return self.saves.write(record)
