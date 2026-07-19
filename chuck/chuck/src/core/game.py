"""The Game class: window, clock, and the main loop.

Responsibilities:
    * Initialize and shut down pygame.
    * Own the window and the native (low-res) render surface.
    * Run the fixed-cadence main loop: events -> update -> draw.
    * Delegate all actual game behavior to the SceneManager.

This class should never contain gameplay logic. If a change here is
needed to add a feature, the feature probably belongs in a scene,
system, or entity instead.
"""

import os
from pathlib import Path

import pygame

# Presentation must stay pixel-perfect: on Windows, DPI display scaling
# (125%/150%) bitmap-stretches DPI-unaware windows by a non-integer
# factor, which makes static pixel art shimmer/crawl during camera
# scrolling. Declaring DPI awareness (before SDL creates the window)
# keeps our 4x nearest-neighbor output exactly 4x on screen.
os.environ.setdefault("SDL_WINDOWS_DPI_AWARENESS", "permonitorv2")

from src.core import config
from src.core.assets import AssetManager
from src.core.input import InputManager
from src.core.scene_manager import SceneManager
from src.systems.audio import AudioSystem
from src.systems.checkpoints import (
    OPENING_CHECKPOINT_ID, CheckpointLoader, ProgressState,
)
from src.systems.cigarettes import CigaretteLedger
from src.systems.save import SaveSystem
from src.scenes.boot_scene import BootScene


class Game:
    """Top-level application object. Created once, in main.py."""

    def __init__(self, save_path: str | Path | None = None) -> None:
        """Initialize pygame, the window, and core managers."""
        # Match the mixer to our rendered audio before pygame.init.
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2,
                              buffer=512)
        pygame.init()

        # vsync is best-effort (silently ignored where unsupported);
        # where honored it removes the tearing ripple during scroll.
        self.window = pygame.display.set_mode(
            (config.WINDOW_WIDTH, config.WINDOW_HEIGHT), vsync=1
        )
        pygame.display.set_caption(config.GAME_TITLE)

        # Everything is drawn to this small surface, then scaled to the
        # window. This is what keeps the pixel art chunky and uniform.
        self.native_surface = pygame.Surface(
            (config.NATIVE_WIDTH, config.NATIVE_HEIGHT)
        )

        self.clock = pygame.time.Clock()
        self.running = False

        self.input = InputManager()
        self.assets = AssetManager()
        self.audio = AudioSystem(self.assets)
        self.scenes = SceneManager(self)
        self.progress = ProgressState()
        self.cigarettes = CigaretteLedger()
        self.active_checkpoint_id = OPENING_CHECKPOINT_ID
        self.saves = SaveSystem(save_path)
        self.checkpoints = CheckpointLoader(self, self.saves)

        # One black frame lets core systems settle before the title menu.
        self.scenes.push(BootScene(self))

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    def run(self) -> None:
        """Run the main loop until quit is requested, then shut down."""
        self.running = True
        while self.running:
            # tick caps the rate; vsync (when honored) paces the flip.
            # The min() keeps their occasional disagreements (missed
            # vblanks, hiccups) from becoming simulation lurches.
            dt = min(self.clock.tick(config.FPS) / 1000.0, config.MAX_DT)
            self._handle_events()
            self._update(dt)
            self._draw()
        self._shutdown()

    def quit(self) -> None:
        """Request a clean exit at the end of the current frame."""
        self.running = False

    # ------------------------------------------------------------------
    # Loop phases
    # ------------------------------------------------------------------
    def _handle_events(self) -> None:
        """Pump the pygame event queue and route events."""
        self.input.begin_frame()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
                continue
            self.input.process_event(event)
            self.scenes.handle_event(event)

    def _update(self, dt: float) -> None:
        """Advance game state by dt seconds."""
        self.scenes.update(dt)

    def _draw(self) -> None:
        """Draw the current frame: scene -> native surface -> window."""
        self.scenes.draw(self.native_surface)
        pygame.transform.scale(
            self.native_surface, self.window.get_size(), self.window
        )
        pygame.display.flip()

    # ------------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------------
    def _shutdown(self) -> None:
        """Release resources and close cleanly."""
        # TODO: Save any persistent state here once saving exists.
        pygame.quit()
