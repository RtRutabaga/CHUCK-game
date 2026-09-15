"""The end credits: a cast roll, the docks one last time, and the cat.

After the ending's fade, the way games of the era did it: the cast rolls
up the screen in the order Chuck met them, each one beside its own sprite
with one line apiece, over slow pans of the places they were met. Then
the docks in the evening -- the opening's own shot -- and how it looks
depends on the smokes: with all three cartons, Bobert is up and they are
both smoking; without, Bobert is asleep again and Chuck smokes alone.
Then the numbers, THE END, and a few seconds of the cat.

It is a cast, not a crew: nobody who made the game is named.

It all plays over the Fall to Chult cue rearranged as upbeat ska.

Holding interact runs it faster; it cannot be skipped outright. Returns
to the title when it is done.
"""

from __future__ import annotations

import math
from typing import NamedTuple

import pygame

from src.core import config
from src.scenes.opening_cutscene_scene import (
    _BARREL_BASE, _BARREL_X, _CHUCK_X, _CHUCK_Y, DRAG, OpeningCutsceneScene)
from src.scenes.scene import Scene


class Sprite(NamedTuple):
    path: str
    frame_w: int
    frame_h: int
    col: int = 0
    row: int = 0


class Member(NamedTuple):
    name: str
    line: str
    sprite: Sprite | None


class Section(NamedTuple):
    title: str
    map_name: str
    focus: tuple[int, int]          # the tile the backdrop pans across
    members: tuple[Member, ...]


def _npc(name: str, width: int = 16) -> Sprite:
    return Sprite(f"npcs/{name}.png", width, 30)


def _hazard(name: str, w: int = 16, h: int = 30, col: int = 0,
            row: int = 0) -> Sprite:
    return Sprite(f"hazards/{name}.png", w, h, col, row)


CAST: tuple[Section, ...] = (
    Section("WATERDEEP", "waterdeep_docks", (12, 13), (
        Member("Chuck", "A rat.",
               Sprite(config.CHUCK_SHEET, config.CHUCK_FRAME_W,
                      config.CHUCK_FRAME_H)),
        Member("Bobert", "Himself. Mostly asleep.",
               Sprite("objects/bobert_barrel.png", 16, 24)),
        Member("The Dock Worker", "Still here.", _npc("dock_worker")),
        Member("The Market Woman", "No handouts.", _npc("market_woman")),
        Member("The Guards", "Stick to the docks, rat.", _npc("guard")),
        Member("The Fisherman", "They're not biting.", _npc("dock_worker")),
        Member("The Cat", "Watch out for it.",
               _hazard("cat", config.CAT_FRAME_W, config.CAT_FRAME_H)),
        Member("The Blacksmith", "Does not shoe rats.", _npc("dock_worker")),
        Member("The Alchemist", "No samples.", _npc("market_woman")),
    )),
    Section("THE SEWER", "sewer", (35, 18), (
        Member("The Rats", "No relation.",
               _hazard("rat", config.RAT_FRAME_W, config.RAT_FRAME_H)),
    )),
    Section("THE TAVERN", "waterdeep_tavern", (10, 8), (
        Member("The Bartender", "Mentioned the cheese.", _npc("bartender")),
        Member("The Patron", "Out of stew.", _npc("patron")),
        Member("The Musician", "Rendition four. The kazoo one.",
               _npc("musician")),
        Member("The Cheese", "It is cheese.",
               Sprite("objects/cheese.png", 10, 7)),
    )),
    Section("CHULT", "chult_falls", (24, 8), (
        Member("The Zombies", "Slow.", _hazard("zombie")),
        Member("The Sailor", "Walkin' on the sea...", _npc("sailor")),
        Member("The Raptors", "Not slow.",
               _hazard("raptor", config.RAPTOR_FRAME_W,
                       config.RAPTOR_FRAME_H, col=2)),
        Member("The Massive Dinosaur", "Big.",
               _hazard("massive_dinosaur", 72, 60)),
        Member("The Tortle", "Piss off!", _npc("tortle", 24)),
    )),
    Section("THE TEMPLE", "temple_entrance", (15, 12), (
        Member("The Skeletons", "Rattling.", _hazard("skeleton")),
        Member("The Snakes", "In a temple. Naturally.",
               _hazard("snake", config.SNAKE_FRAME_W, config.SNAKE_FRAME_H)),
        Member("The Beholder", "Kept its eye off them.",
               Sprite("npcs/beholder.png", 40, 40)),
        Member("The Fighter", "Held the line.", _npc("fighter")),
        Member("The Wizard", "Needed another minute.", _npc("wizard")),
        Member("The Ranger", "Kept them off him.", _npc("ranger")),
    )),
    Section("THE SHIP", "ship_exterior_deck", (20, 12), (
        Member("The Pirate Chef", "Come er' you little bugger!",
               Sprite("hazards/pirate_chef.png", 16, 30)),
        Member("The Seated Pirate", "Never seen a rat in a coat.",
               _npc("seated_pirate")),
        Member("The Concertina Pirate", "Still considering it.",
               _npc("concertina_pirate")),
        Member("The Cheering Pirate", "Don't mind Jeffries.",
               _npc("cheering_pirate")),
        Member("The Dancing Pirate", "Other half's his.",
               _npc("dancing_pirate")),
        Member("Jeffries", "Don't go into the purple!", _npc("jeffries")),
        Member("The Swordsmen", "Busy.",
               Sprite("hazards/sword_fighter_a.png", 24, 30)),
        Member("The Captain", "The plank.", _npc("captain_pirate")),
    )),
    Section("PHLEGETHOS", "phlegethos_road", (20, 12), (
        Member("The Lemures", "Lumpy.", _hazard("lemure")),
        Member("The Fire Snakes", "Snakes, but on fire.",
               _hazard("fire_snake", config.SNAKE_FRAME_W,
                       config.SNAKE_FRAME_H)),
        Member("The Flameskulls", "Skulls, but on fire.",
               _hazard("flameskull", config.FLAMESKULL_FRAME_W,
                       config.FLAMESKULL_FRAME_H)),
        Member("The Spined Devils", "Spiny.",
               _hazard("spined_devil", config.SPINED_DEVIL_FRAME_W,
                       config.SPINED_DEVIL_FRAME_H)),
        Member("The Horned Devils", "Horned.",
               _hazard("horned_devil", 72, 60)),
        Member("The Pit Fiend", "Enormous.",
               Sprite("npcs/pit_fiend.png", 128, 128)),
    )),
    Section("THE FEYWILD", "feywild_blooming_path", (20, 12), (
        Member("The Redcaps", "Red caps.",
               _hazard("redcap", config.REDCAP_FRAME_W,
                       config.REDCAP_FRAME_H)),
        Member("The Thorn Mites", "Small. Thorny.",
               _hazard("thorn_mite", config.RAT_FRAME_W,
                       config.RAT_FRAME_H)),
        Member("The Spitting Orchids", "Spitting.",
               _hazard("spitting_orchid", config.ORCHID_FRAME_W,
                       config.ORCHID_FRAME_H)),
        Member("The Lantern Moths", "Glowing.",
               _hazard("lantern_moth", 18, 18)),
        Member("The Displacer Beasts", "Not where they look.",
               _hazard("displacer_beast", 72, 60)),
    )),
    Section("ZEPHYROS", "zephyros_tower_exterior", (20, 14), (
        Member("Zephyros", "Hello little friend!", None),
        Member("The Griffons", "Nesting.", _hazard("griffon", 72, 60)),
    )),
    Section("THE CITY", "modern_city_night_3", (24, 14), (
        Member("The Businessmen", "Ah! A rat!", _npc("businessman")),
        Member("The Woman in Red", "Ah! A rat!", _npc("red_dress_woman")),
        Member("The Homeless Man", "Hey there buddy!",
               _npc("homeless_man")),
        Member("The Raccoons", "Distant relations.",
               _hazard("raccoon", config.RACCOON_FRAME_W,
                       config.RACCOON_FRAME_H)),
        Member("The Sewer Crocodile", "It's true.", _hazard("crocodile")),
        Member("The Police", "Called about a rat.",
               _hazard("police", config.POLICE_FRAME_W,
                       config.POLICE_FRAME_H)),
        Member("Animal Control", "Also called about a rat.",
               _hazard("animal_control")),
        Member("Traffic", "Did not stop.",
               Sprite("hazards/city_traffic.png", 40, 20)),
    )),
    Section("THE CABIN", "tahuya_cabin_exterior", (62, 31), (
        Member("The Lights", "Said something. Unclear what.",
               Sprite("npcs/cabin_light_entity.png", 28, 30)),
        Member("The Goose", "Winked. Probably.",
               Sprite("objects/cabin_goose_mount.png", 0, 0)),
    )),
    Section("THE DESERT", "desert_central", (24, 16), (
        Member("The Orcs", "Camping.", _hazard("orc")),
        Member("The Knights", "Swords out.", _hazard("knight")),
        Member("The Blue Dragon", "Lightning, mostly.",
               _hazard("blue_dragon", 128, 96)),
        Member("The Red Dragon", "Fire, entirely.",
               _hazard("red_dragon", 128, 96)),
    )),
    Section("AND", "waterdeep_docks", (12, 13), (
        Member("Premium Buhetian Halfling Leaf", "Three cartons.",
               Sprite("objects/golden_cigarette_carton.png", 0, 0)),
    )),
)

# The Fall to Chult cue, as ska (data/music/credits_ska.py).
CREDITS_MUSIC = "credits_ska.wav"
VIEW_W, VIEW_H = config.NATIVE_WIDTH, config.NATIVE_HEIGHT
SCROLL_SPEED = 22.0          # px per second
FAST = 6.0                   # while interact is held
SPRITE_RIGHT = 122           # sprites end here, left of the names
TEXT_X = 132
MAX_CAST_H = 64              # anything taller or wider is halved
MAX_CAST_W = 64
MEMBER_GAP = 14
SECTION_GAP = 40
BACKDROP_DIM = 190           # alpha of the black over the backdrops
BACKDROP_PAN = 160           # px the backdrop drifts across a section
CROSSFADE = 1.4

TABLEAU = 9.0                # the docks, one last time
STATS = 7.0
THE_END = 5.0
STINGER = 4.5
PAGE_FADE = 1.2
CLOSE_UP = (85, 56, 160, 90)   # of the opening's frame, shown at 2x

NAME_TINT = (246, 214, 140)
LINE_ALPHA = 190


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def stats_lines(deaths: int, cigarettes: int, cartons: int,
                total: int) -> list[tuple[str, str]]:
    """The numbers, and a word on each."""
    if deaths == 0:
        died = "Not once. Remarkable."
    elif deaths == 1:
        died = "Just the once."
    else:
        died = "Rats have short lives."
    smoked = "Not one." if cigarettes == 0 else "Worth it."
    carried = ("Bobert is thrilled." if cartons >= total
               else "Bobert noticed.")
    return [
        (f"Deaths: {deaths}", died),
        (f"Cigarettes: {cigarettes}", smoked),
        (f"Premium cartons: {cartons}/{total}", carried),
    ]


class _DocksTableau(OpeningCutsceneScene):
    """The opening's evening shot, held on its smoking beat.

    Borrowed rather than redrawn so the last image of the game is the
    first one, changed only by what Chuck brought home.
    """

    def __init__(self, game, *, good: bool, chuck: bool = True,
                 cat: bool = False) -> None:
        super().__init__(game)
        self.good = good
        self.chuck = chuck
        self.cat = cat
        self._cat_frame: pygame.Surface | None = None

    def on_enter(self) -> None:
        # The opening's loading, without its music cue or hand-off.
        audio = self.game.audio
        stop = audio.stop_music
        audio.stop_music = lambda fade_ms=0: None
        try:
            super().on_enter()
        finally:
            audio.stop_music = stop
        if self.good:
            self._barrel = self._image("objects/bobert_barrel_awake.png") \
                or self._barrel
        try:
            self._cat_frame = self.game.assets.sheet(
                config.CAT_SHEET, config.CAT_FRAME_W, config.CAT_FRAME_H
            )[0][2]
        except (FileNotFoundError, pygame.error, IndexError):
            self._cat_frame = None

    def advance(self, dt: float) -> None:
        self.elapsed += dt

    def _play_cues(self, previous: float, current: float) -> None:
        return

    def draw(self, surface: pygame.Surface) -> None:
        self._draw_sky_and_water(surface)
        if self._boat is not None:
            from src.scenes.opening_cutscene_scene import _BOAT_X, _BOAT_Y
            surface.blit(self._boat, (_BOAT_X, _BOAT_Y))
        self._draw_quay(surface)
        self._draw_moorings(surface)
        self._draw_bobert_and_chuck(surface)

    def _draw_bobert_and_chuck(self, surface: pygame.Surface) -> None:
        if self._barrel is not None:
            surface.blit(self._barrel, (_BARREL_X, _BARREL_BASE
                                        - self._barrel.get_height()))
        if self.good:
            self._draw_bobert_smoking(surface)
        else:
            self._draw_zs(surface, (_BARREL_X + 13, _BARREL_BASE - 28),
                          2.1, 4)
        if self.chuck:
            frame = self._frames.get("left")
            if frame is not None:
                surface.blit(frame, (_CHUCK_X, _CHUCK_Y))
            self._draw_smoke(surface)
        if self.cat and self._cat_frame is not None:
            cat = pygame.transform.flip(self._cat_frame, True, False)
            surface.blit(cat, (_CHUCK_X - 10,
                               _BARREL_BASE - cat.get_height()))

    def _draw_bobert_smoking(self, surface: pygame.Surface) -> None:
        """A cigarette out of the beard, and his own smoke going up."""
        mouth = (_BARREL_X + 11, _BARREL_BASE - 24 + 6)
        surface.fill((236, 236, 228), (mouth[0], mouth[1], 3, 1))
        surface.set_at((mouth[0] + 3, mouth[1]), (242, 146, 66))
        tip = (mouth[0] + 3, mouth[1] - 1)
        for puff in range(3):
            t = ((self.elapsed - 1.7) * 0.45 + puff / 3) % 1.0
            x = round(tip[0] + t * 4 + math.sin(t * 5 + puff) * 1.5)
            y = round(tip[1] - 1 - t * 16)
            shade = 150 + round(60 * (1 - t))
            if t < 0.85:
                surface.set_at((x, y), (shade, shade, shade - 6))


class CreditsScene(Scene):
    """Cast roll, final image, numbers, THE END, the cat, the title."""

    def __init__(self, game, *, good: bool) -> None:
        super().__init__(game)
        self.good = good
        self.elapsed = 0.0
        self.scroll = 0.0
        self.finished = False
        self._font = game.assets.bitmap_font()
        self._rows: list[tuple[float, pygame.Surface]] = []
        self._section_tops: list[float] = []
        self._height = 0.0
        self._backdrops: dict[int, pygame.Surface | None] = {}
        self._shown = 0
        self._previous = 0
        self._switched_at = -CROSSFADE
        self._tail = 0.0            # seconds since the roll ran out
        self._tableau: _DocksTableau | None = None
        self._stinger: _DocksTableau | None = None

    # ------------------------------------------------------------------
    def on_enter(self) -> None:
        self.game.audio.play_music(CREDITS_MUSIC)
        self._build_roll()
        self._tableau = _DocksTableau(self.game, good=self.good)
        self._tableau.on_enter()
        self._tableau.elapsed = DRAG + 0.5
        self._stinger = _DocksTableau(self.game, good=self.good,
                                      chuck=False, cat=True)
        self._stinger.on_enter()
        self._stinger.elapsed = DRAG + 0.5

    def _text(self, text: str, tint=None, alpha: int = 255):
        surface = self._font.render(text)
        if tint is not None:
            surface = surface.copy()
            surface.fill((*tint, 255), special_flags=pygame.BLEND_RGBA_MULT)
        surface.set_alpha(alpha)
        return surface

    def _cast_image(self, sprite: Sprite | None, name: str):
        if sprite is None:
            if name == "Zephyros":
                return self._zephyros()
            return None
        assets = self.game.assets
        try:
            if sprite.frame_w == 0:
                image = assets.image(sprite.path)
            else:
                image = assets.sheet(sprite.path, sprite.frame_w,
                                     sprite.frame_h)[sprite.row][sprite.col]
        except (FileNotFoundError, pygame.error, IndexError, KeyError):
            return None
        while (image.get_height() > MAX_CAST_H
               or image.get_width() > MAX_CAST_W):
            image = pygame.transform.scale(
                image, (image.get_width() // 2, image.get_height() // 2))
        return image

    def _zephyros(self):
        """The cloud giant's face, from his own cutscene, made small."""
        try:
            from src.scenes.zephyros_intro_cutscene_scene import (
                ZephyrosIntroCutsceneScene)
            scene = ZephyrosIntroCutsceneScene.__new__(
                ZephyrosIntroCutsceneScene)
            scene.game = self.game
            scene.elapsed = 30.0
            big = pygame.Surface((240, 240), pygame.SRCALPHA)
            scene._draw_zephyros(big, 46, 10)
            big = big.subsurface((0, 0, 240, 200)).copy()
            return pygame.transform.scale(big, (48, 40))
        except Exception:  # decoration only; the name still rolls
            return None

    def _build_roll(self) -> None:
        y = float(VIEW_H)
        for index, section in enumerate(CAST):
            if index:
                y += SECTION_GAP
            self._section_tops.append(y)
            title = self._text(section.title, NAME_TINT)
            self._rows.append((y, title, (VIEW_W - title.get_width()) // 2))
            y += title.get_height() + MEMBER_GAP + 4
            for member in section.members:
                image = self._cast_image(member.sprite, member.name)
                name = self._text(member.name, NAME_TINT)
                line = self._text(member.line, alpha=LINE_ALPHA)
                text_h = name.get_height() + 2 + line.get_height()
                height = max(text_h, image.get_height() if image else 0)
                if image is not None:
                    self._rows.append((
                        y + height - image.get_height(), image,
                        SPRITE_RIGHT - image.get_width()))
                text_top = y + (height - text_h) / 2
                self._rows.append((text_top, name, TEXT_X))
                self._rows.append((text_top + name.get_height() + 2, line,
                                   TEXT_X))
                y += height + MEMBER_GAP
        self._height = y

    # ------------------------------------------------------------------
    @property
    def roll_done(self) -> bool:
        return self.scroll >= self._height

    @property
    def page(self) -> str:
        """Which part of the credits is on screen."""
        if not self.roll_done:
            return "cast"
        t = self._tail
        for name, length in (("tableau", TABLEAU), ("stats", STATS),
                             ("the_end", THE_END), ("stinger", STINGER)):
            if t < length:
                return name
            t -= length
        return "done"

    def _page_time(self) -> tuple[float, float]:
        t = self._tail
        for length in (TABLEAU, STATS, THE_END, STINGER):
            if t < length:
                return t, length
            t -= length
        return 0.0, 1.0

    def update(self, dt: float) -> None:
        if self.finished:
            return
        speed = FAST if self.game.input.is_down("interact") else 1.0
        dt *= speed
        self.elapsed += dt
        if not self.roll_done:
            self.scroll = min(self._height, self.scroll + SCROLL_SPEED * dt)
            current = self._current_section()
            if current != self._shown:
                self._previous, self._shown = self._shown, current
                self._switched_at = self.elapsed
            return
        self._tail += dt
        if self._tableau is not None:
            self._tableau.advance(dt)
        if self._stinger is not None:
            self._stinger.advance(dt)
        if self.page == "done":
            self.finished = True
            from src.scenes.title_scene import TitleScene
            scenes = self.game.scenes
            while scenes.current is not None:
                scenes.pop()
            scenes.push(TitleScene(self.game))

    def _current_section(self) -> int:
        middle = self.scroll + VIEW_H / 2
        current = 0
        for index, top in enumerate(self._section_tops):
            if top <= middle:
                current = index
        return current

    # ------------------------------------------------------------------
    def _backdrop(self, index: int):
        if index not in self._backdrops:
            section = CAST[index]
            try:
                self._backdrops[index] = render_backdrop(
                    self.game, section.map_name, section.focus)
            except Exception:  # a missing backdrop is just black
                self._backdrops[index] = None
        return self._backdrops[index]

    def _draw_backdrop(self, surface, index: int, alpha: int) -> None:
        image = self._backdrop(index)
        if image is None or alpha <= 0:
            return
        top = self._section_tops[index]
        end = (self._section_tops[index + 1]
               if index + 1 < len(self._section_tops) else self._height)
        span = max(1.0, end - top + VIEW_H)
        progress = _clamp01((self.scroll + VIEW_H - top) / span)
        x = -round(progress * (image.get_width() - VIEW_W))
        image.set_alpha(alpha)
        surface.blit(image, (x, 0))
        image.set_alpha(None)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((0, 0, 0))
        page = self.page
        if page == "cast":
            self._draw_cast(surface)
        elif page == "tableau":
            self._draw_page(surface, self._close_up(self._tableau))
        elif page == "stats":
            self._draw_page(surface, self._draw_stats)
        elif page == "the_end":
            self._draw_page(surface, self._draw_the_end)
        elif page == "stinger":
            self._draw_page(surface, self._close_up(self._stinger))

    @staticmethod
    def _close_up(tableau):
        """The opening's wide shot, closer: the barrel, the pair, the dusk."""
        def paint(surface):
            wide = pygame.Surface((VIEW_W, VIEW_H))
            tableau.draw(wide)
            crop = wide.subsurface(CLOSE_UP)
            surface.blit(pygame.transform.scale(crop, (VIEW_W, VIEW_H)),
                         (0, 0))
        return paint

    def _draw_page(self, surface, painter) -> None:
        painter(surface)
        t, length = self._page_time()
        amount = max(1.0 - t / PAGE_FADE, (t - (length - PAGE_FADE))
                     / PAGE_FADE)
        if amount > 0:
            veil = pygame.Surface(surface.get_size())
            veil.set_alpha(round(255 * _clamp01(amount)))
            surface.blit(veil, (0, 0))

    def _draw_cast(self, surface) -> None:
        fade = _clamp01((self.elapsed - self._switched_at) / CROSSFADE)
        if fade < 1.0:
            self._draw_backdrop(surface, self._previous, 255)
        self._draw_backdrop(surface, self._shown, round(255 * fade))
        veil = pygame.Surface(surface.get_size())
        veil.set_alpha(BACKDROP_DIM)
        surface.blit(veil, (0, 0))
        # The roll fades in over the first seconds, out of the ending.
        for top, image, x in self._rows:
            y = round(top - self.scroll)
            if -image.get_height() < y < VIEW_H:
                surface.blit(image, (x, y))
        if self.elapsed < 2.0:
            veil.set_alpha(round(255 * (1 - self.elapsed / 2.0)))
            surface.blit(veil, (0, 0))

    def _draw_stats(self, surface) -> None:
        from src.entities.captain_chest import (
            PREMIUM_CARTON_FLAGS, premium_cartons_collected)
        lines = stats_lines(
            self.game.deaths.total, self.game.cigarettes.total,
            premium_cartons_collected(self.game.progress),
            len(PREMIUM_CARTON_FLAGS))
        y = VIEW_H // 2 - (len(lines) * 26) // 2
        for figure, remark in lines:
            head = self._text(figure, NAME_TINT)
            tail = self._text(remark, alpha=LINE_ALPHA)
            surface.blit(head, ((VIEW_W - head.get_width()) // 2, y))
            surface.blit(tail, ((VIEW_W - tail.get_width()) // 2, y + 11))
            y += 26

    def _draw_the_end(self, surface) -> None:
        text = self._text("THE END")
        text = pygame.transform.scale(
            text, (text.get_width() * 2, text.get_height() * 2))
        surface.blit(text, ((VIEW_W - text.get_width()) // 2,
                            (VIEW_H - text.get_height()) // 2))


def render_backdrop(game, map_name: str, focus: tuple[int, int]):
    """A strip of a real map around a tile, drawn the way the world draws.

    Wider than the screen by BACKDROP_PAN so it can drift across a section.
    Ground, the props that stand on it, and the overhead layer; nobody in
    it. Props that need a live scene to exist are left out.
    """
    from src.entities.prop import Prop
    from src.world.tilemap import TileMap
    from src.world.tileset_layout import tileset_for

    tilemap = TileMap(config.MAPS_DIR / f"{map_name}.txt")
    tilemap.load_tileset(game.assets, tileset_for(map_name))
    ts = config.TILE_SIZE
    map_w, map_h = tilemap.width_tiles * ts, tilemap.height_tiles * ts
    # As wide as the pan wants, but no wider than the map has to give:
    # a small room holds still rather than drifting into black.
    width = max(VIEW_W, min(VIEW_W + BACKDROP_PAN, map_w))
    height = VIEW_H
    left = int(focus[0] * ts + ts / 2 - width / 2)
    top = int(focus[1] * ts + ts / 2 - height / 2)
    left = (max(0, min(left, map_w - width)) if map_w >= width
            else -(width - map_w) // 2)
    top = (max(0, min(top, map_h - height)) if map_h >= height
           else -(height - map_h) // 2)
    offset = (left, top)
    surface = pygame.Surface((width, height))
    surface.fill((0, 0, 0))
    tilemap.draw_ground(surface, offset, 0.0)
    props = []
    for kind, col, row in tilemap.prop_tiles:
        x, y = col * ts, row * ts
        if not (left - 160 < x < left + width + 160
                and top - 40 < y < top + height + 200):
            continue
        try:
            props.append(Prop(kind, col, row, game.assets))
        except (ValueError, FileNotFoundError, pygame.error):
            continue
    for prop in props:
        if getattr(prop, "floor_layer", False):
            prop.draw(surface, offset)
    for prop in sorted(props, key=lambda p: p.sort_y):
        if not getattr(prop, "floor_layer", False):
            prop.draw(surface, offset)
    tilemap.draw_overhead(surface, offset, 0.0)
    return surface
