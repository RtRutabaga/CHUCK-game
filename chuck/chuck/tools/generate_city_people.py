"""Generate the Phase 11 businessperson sprite sheet."""

import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame


ROOT = Path(__file__).resolve().parents[1]
W, H = 16, 30


def draw_person(surface: pygame.Surface, facing: str) -> None:
    # Umbrella, head, dark suit, shirt and human-scale shoes; kept readable
    # in the same 16x30 silhouette as Waterdeep's NPCs.
    pygame.draw.ellipse(surface, (27, 31, 42), (0, 0, 16, 7))
    pygame.draw.rect(surface, (17, 19, 26), (7, 4, 2, 11))
    skin = (202, 159, 121)
    pygame.draw.rect(surface, skin, (5, 7, 6, 6))
    pygame.draw.rect(surface, (38, 44, 56), (4, 13, 8, 11))
    pygame.draw.rect(surface, (213, 215, 207), (7, 13, 2, 7))
    pygame.draw.rect(surface, (27, 29, 37), (4, 23, 3, 6))
    pygame.draw.rect(surface, (27, 29, 37), (9, 23, 3, 6))
    if facing == "down":
        pygame.draw.rect(surface, (73, 52, 39), (6, 8, 4, 2))
        pygame.draw.rect(surface, (38, 32, 27), (6, 11, 1, 1))
        pygame.draw.rect(surface, (38, 32, 27), (9, 11, 1, 1))
    elif facing == "up":
        pygame.draw.rect(surface, (73, 52, 39), (5, 7, 6, 3))
    else:
        pygame.draw.rect(surface, (73, 52, 39), (5, 7, 5, 3))
        pygame.draw.rect(surface, (38, 32, 27), (5, 10, 1, 1))


def draw_homeless_man(surface: pygame.Surface, facing: str) -> None:
    """A quiet seated human silhouette, anchored to the same NPC frame."""
    skin = (183, 137, 105)
    coat = (89, 75, 66)
    dark = (38, 38, 43)
    pygame.draw.rect(surface, (56, 62, 74), (5, 8, 7, 3))  # knit cap
    pygame.draw.rect(surface, skin, (6, 11, 5, 5))
    pygame.draw.polygon(surface, coat, ((4, 16), (11, 15), (13, 24), (3, 24)))
    pygame.draw.rect(surface, dark, (2, 23, 6, 4))
    pygame.draw.rect(surface, dark, (9, 23, 6, 4))
    pygame.draw.rect(surface, (31, 32, 37), (1, 27, 7, 2))
    pygame.draw.rect(surface, (31, 32, 37), (9, 27, 7, 2))
    if facing == "down":
        pygame.draw.rect(surface, (67, 49, 39), (7, 12, 3, 2))
        pygame.draw.rect(surface, (34, 29, 27), (7, 14, 1, 1))
        pygame.draw.rect(surface, (34, 29, 27), (9, 14, 1, 1))
    elif facing == "up":
        pygame.draw.rect(surface, (67, 49, 39), (6, 11, 5, 3))
    else:
        pygame.draw.rect(surface, (67, 49, 39), (6, 11, 4, 3))


def draw_bottles(surface: pygame.Surface, variant: int) -> None:
    colours = ((74, 116, 92), (113, 83, 48), (55, 94, 113))
    placements = (
        ((1, 5, 4, 10), (7, 8, 4, 7), (12, 4, 3, 11)),
        ((1, 8, 3, 7), (5, 3, 4, 12), (11, 7, 4, 8)),
    )[variant]
    for index, (x, y, w, h) in enumerate(placements):
        colour = colours[(index + variant) % len(colours)]
        pygame.draw.rect(surface, (20, 23, 28, 110), (x, 13, w, 2))
        pygame.draw.rect(surface, colour, (x, y + 3, w, h - 3))
        pygame.draw.rect(surface, colour, (x + 1, y, max(1, w - 2), 4))
        pygame.draw.rect(surface, (157, 176, 151), (x + 1, y + 4, 1, 3))


def main() -> None:
    pygame.init()
    sheet = pygame.Surface((W * 3, H), pygame.SRCALPHA)
    for index, facing in enumerate(("down", "up", "left")):
        frame = pygame.Surface((W, H), pygame.SRCALPHA)
        draw_person(frame, facing)
        sheet.blit(frame, (index * W, 0))
    output = ROOT / "assets" / "sprites" / "npcs" / "businessman.png"
    pygame.image.save(sheet, output)
    print(f"Wrote {output} ({W * 3}x{H})")

    homeless = pygame.Surface((W * 3, H), pygame.SRCALPHA)
    for index, facing in enumerate(("down", "up", "left")):
        frame = pygame.Surface((W, H), pygame.SRCALPHA)
        draw_homeless_man(frame, facing)
        homeless.blit(frame, (index * W, 0))
    homeless_output = (
        ROOT / "assets" / "sprites" / "npcs" / "homeless_man.png"
    )
    pygame.image.save(homeless, homeless_output)
    print(f"Wrote {homeless_output} ({W * 3}x{H})")

    for variant in range(2):
        bottles = pygame.Surface((16, 16), pygame.SRCALPHA)
        draw_bottles(bottles, variant)
        bottle_output = (
            ROOT / "assets" / "sprites" / "objects"
            / f"city_bottles_{variant + 1}.png"
        )
        pygame.image.save(bottles, bottle_output)
        print(f"Wrote {bottle_output} (16x16)")


if __name__ == "__main__":
    main()
