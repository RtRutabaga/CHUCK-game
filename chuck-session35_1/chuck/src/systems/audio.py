"""Audio playback.

Responsibilities:
    * Loop the area ambience (later: music) via pygame.mixer.music.
    * Fire one-shot SFX through cached Sound objects.
    * Own volume levels; gameplay code never touches pygame.mixer.

Degrades gracefully: if the mixer can't initialize (no audio device,
headless CI), the game runs silently with one console warning instead
of crashing. The game must always launch.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from src.core import config

if TYPE_CHECKING:
    from src.core.assets import AssetManager


class AudioSystem:
    """Central music/SFX playback. One instance, owned by Game."""

    def __init__(self, assets: "AssetManager") -> None:
        self._assets = assets
        self.enabled = pygame.mixer.get_init() is not None
        if not self.enabled:
            try:
                pygame.mixer.init()
                self.enabled = True
            except pygame.error as exc:
                print(f"[audio] disabled (no mixer): {exc}")
        self.music_volume = config.AUDIO_MUSIC_VOLUME
        self.sfx_volume = config.AUDIO_SFX_VOLUME

    # ------------------------------------------------------------------
    # Streams (ambience / music)
    # ------------------------------------------------------------------
    def play_music(self, filename: str, loop: bool = True) -> None:
        """Stream a track from assets/audio/music/, looping by default.

        TODO (later): crossfades between area themes / variations.
        """
        if not self.enabled:
            return
        path = config.MUSIC_DIR / filename
        if not path.is_file():
            raise FileNotFoundError(
                f"Missing music {path}. Run: python tools/generate_music.py"
            )
        pygame.mixer.music.load(str(path))
        pygame.mixer.music.set_volume(self.music_volume)
        pygame.mixer.music.play(-1 if loop else 0)

    def stop_music(self, fade_ms: int = 0) -> None:
        if not self.enabled:
            return
        if fade_ms > 0:
            pygame.mixer.music.fadeout(fade_ms)
        else:
            pygame.mixer.music.stop()

    # ------------------------------------------------------------------
    # One-shots
    # ------------------------------------------------------------------
    def play_sfx(self, name: str) -> None:
        """Fire a one-shot from assets/audio/sfx/ (name without .wav)."""
        if not self.enabled:
            return
        sound = self._assets.sound(f"{name}.wav")
        sound.set_volume(self.sfx_volume)
        sound.play()
