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
from src.systems.deaths import DeathCounter
from src.systems.save import SaveSystem
from src.systems.settings import DEFAULT_LEVEL, SettingsStore
from src.scenes.boot_scene import BootScene


class Game:
    """Top-level application object. Created once, in main.py."""

    def __init__(self, save_path: str | Path | None = None) -> None:
        """Initialize pygame, the window, and core managers."""
        # Match the mixer to our rendered audio before pygame.init.
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2,
                              buffer=512)
        pygame.init()

        # The player's settings live beside the save slot (not in it:
        # NEW GAME wipes the save, and should not reset the volume).
        self.saves = SaveSystem(save_path)
        self.settings_store = SettingsStore(
            self.saves.path.with_name("settings.json"))
        self.settings = self.settings_store.load()

        self.window = self._open_window(self.settings.fullscreen)
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
        self.audio.set_levels(self.settings.music / DEFAULT_LEVEL,
                              self.settings.sound / DEFAULT_LEVEL)
        self.scenes = SceneManager(self)
        self.progress = ProgressState()
        self.cigarettes = CigaretteLedger()
        self.deaths = DeathCounter()
        # People Chuck has already had a first word from this session.
        self.spoken_to: set[tuple] = set()
        self.active_checkpoint_id = OPENING_CHECKPOINT_ID
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
    # Window and settings
    # ------------------------------------------------------------------
    @staticmethod
    def _open_window(fullscreen: bool, vsync: bool = True):
        """A resizable window, or the desktop at full size.

        vsync is best-effort (silently ignored where unsupported); where
        honoured it removes the tearing ripple during scroll. It is only
        asked for when the window is first opened: recreating a vsynced
        window to switch modes crashes SDL's renderer on some drivers, so
        a switch keeps the clock's 60fps cap and drops the vsync request.
        If the display will not give us fullscreen, the window is the
        fallback rather than a crash.
        """
        extra = {"vsync": 1} if vsync else {}
        if fullscreen:
            try:
                return pygame.display.set_mode((0, 0), pygame.FULLSCREEN,
                                               **extra)
            except pygame.error:
                pass
        try:
            return pygame.display.set_mode(
                (config.WINDOW_WIDTH, config.WINDOW_HEIGHT),
                pygame.RESIZABLE, **extra)
        except pygame.error:
            return pygame.display.set_mode(
                (config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.RESIZABLE)

    def set_fullscreen(self, fullscreen: bool) -> None:
        """Switch between fullscreen and a window, and remember it."""
        self.settings.fullscreen = bool(fullscreen)
        self.window = self._open_window(self.settings.fullscreen,
                                        vsync=False)
        self.settings_store.write(self.settings)

    def set_volume(self, *, music: int | None = None,
                   sound: int | None = None) -> None:
        """Change the music or sound level (0..10), and remember it."""
        if music is not None:
            self.settings.music = music
        if sound is not None:
            self.settings.sound = sound
        self.audio.set_levels(self.settings.music / DEFAULT_LEVEL,
                              self.settings.sound / DEFAULT_LEVEL)
        self.settings_store.write(self.settings)

    def pause(self) -> bool:
        """Open the pause menu over the current scene, if it pauses."""
        from src.scenes.pause_scene import PauseScene

        current = self.scenes.current
        if current is None or not getattr(current, "pausable", False):
            return False
        self.scenes.push(PauseScene(self))
        return True

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
            if event.type == pygame.VIDEORESIZE:
                self.window = pygame.display.get_surface()
                continue
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                self.set_fullscreen(not self.settings.fullscreen)
                continue
            if (event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE and self.pause()):
                continue
            self.input.process_event(event)
            self.scenes.handle_event(event)

    def _update(self, dt: float) -> None:
        """Advance game state by dt seconds."""
        self.scenes.update(dt)

    def _draw(self) -> None:
        """Draw the current frame: scene -> native surface -> window."""
        # A scene may ask for a bigger canvas than the game's native one
        # -- the title does, so Chuck can be drawn with a face -- and it
        # is then scaled up by less instead of by more.
        size = getattr(self.scenes.current, "canvas_size", None)
        target = self.native_surface
        if size and tuple(size) != self.native_surface.get_size():
            canvas = getattr(self, "_scene_canvas", None)
            if canvas is None or canvas.get_size() != tuple(size):
                self._scene_canvas = pygame.Surface(tuple(size))
            target = self._scene_canvas
        self.scenes.draw(target)
        self.window.fill(config.COLOR_BLACK)
        self.window.blit(*self.present(target, self.window.get_size()))
        pygame.display.flip()

    @staticmethod
    def present(target, window_size):
        """The scaled frame and where it goes in a window of any size.

        Whole-number scaling wherever the window is at least the size of
        the canvas, so the pixel art stays pixel-perfect -- 1920x1080 is
        exactly 6x, 2560x1440 exactly 8x -- with black bars for whatever
        is left over. Only a window smaller than the canvas itself is
        scaled by a fraction, because the alternative is cropping it.
        """
        width, height = target.get_size()
        win_w, win_h = window_size
        fit = min(win_w / width, win_h / height)
        scale = int(fit) if fit >= 1 else fit
        size = (max(1, round(width * scale)), max(1, round(height * scale)))
        frame = pygame.transform.scale(target, size)
        return frame, ((win_w - size[0]) // 2, (win_h - size[1]) // 2)

    # ------------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------------
    def _shutdown(self) -> None:
        """Release resources and close cleanly."""
        pygame.quit()
