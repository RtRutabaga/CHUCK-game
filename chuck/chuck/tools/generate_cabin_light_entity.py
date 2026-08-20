"""Generate the Cabin's eight-frame seated light-entity sheet."""

import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame


ROOT = Path(__file__).resolve().parents[1]
FRAME_W = 28
FRAME_H = 30
PALETTE = (
    (198, 105, 151),  # rose
    (145, 103, 190),  # violet
    (91, 125, 194),   # blue
    (80, 168, 184),   # cyan
    (94, 159, 122),   # green
    (180, 166, 83),   # yellow
    (202, 134, 76),   # amber
    (151, 123, 163),  # gray-violet seam
)


def _blend(a, b, amount):
    return tuple(round(x + (y - x) * amount) for x, y in zip(a, b))


def draw_frame(index, facing="south"):
    """A seated humanoid made of gray-biased, smoothly travelling light."""
    surface = pygame.Surface((FRAME_W, FRAME_H), pygame.SRCALPHA)
    main = PALETTE[index]
    next_colour = PALETTE[(index + 2) % len(PALETTE)]
    pale = _blend(main, (210, 211, 207), 0.48)
    shadow = _blend(main, (53, 51, 58), 0.58)

    # Restrained pool of projected light, kept translucent and close to seat.
    glow = pygame.Surface((FRAME_W, FRAME_H), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (*main, 28), (1, 22, 26, 7))
    pygame.draw.ellipse(glow, (*next_colour, 18), (5, 24, 18, 5))
    surface.blit(glow, (0, 0))

    if facing == "west":
        # Side-on seated silhouette: face/nose and both bent knees point left.
        pygame.draw.circle(surface, shadow, (12, 6), 5)
        pygame.draw.circle(surface, pale, (11, 5), 4)
        pygame.draw.rect(surface, pale, (6, 5, 4, 2))
        pygame.draw.polygon(surface, shadow, ((10, 11), (20, 12), (20, 23),
                                              (14, 25), (7, 22)))
        pygame.draw.polygon(surface, main, ((11, 12), (18, 13), (18, 21),
                                           (13, 23), (8, 21)))
        pygame.draw.rect(surface, shadow, (6, 15, 8, 4))
        pygame.draw.rect(surface, pale, (4, 18, 10, 4))
        pygame.draw.rect(surface, shadow, (5, 22, 10, 4))
        pygame.draw.rect(surface, next_colour, (3, 25, 11, 3))
    else:
        # Clear seated silhouette: head, shoulders, torso, forearms and knees.
        pygame.draw.circle(surface, shadow, (14, 6), 5)
        pygame.draw.circle(surface, pale, (14, 5), 4)
        pygame.draw.polygon(surface, shadow, ((7, 11), (21, 11), (23, 22),
                                              (18, 25), (10, 25), (5, 22)))
        pygame.draw.polygon(surface, main, ((8, 12), (20, 12), (20, 21),
                                           (17, 23), (11, 23), (7, 20)))
        pygame.draw.rect(surface, shadow, (4, 13, 4, 10))
        pygame.draw.rect(surface, shadow, (20, 13, 4, 10))
        pygame.draw.rect(surface, pale, (8, 22, 7, 4))
        pygame.draw.rect(surface, next_colour, (15, 22, 6, 4))

    # Broad travelling bands make the tie-dye movement legible at 320x180.
    band_y = 4 + (index * 3) % 17
    for y in range(band_y, min(24, band_y + 3)):
        for x in range(6, 22):
            if surface.get_at((x, y)).a:
                surface.set_at((x, y), (*next_colour, 255))
    pygame.draw.rect(surface, (224, 224, 218), (12, 4, 1, 1))
    pygame.draw.rect(surface, (224, 224, 218), (17, 4, 1, 1))
    return surface


def main():
    pygame.init()
    sheet = pygame.Surface(
        (FRAME_W * len(PALETTE), FRAME_H * 2), pygame.SRCALPHA
    )
    for row, facing in enumerate(("south", "west")):
        for index in range(len(PALETTE)):
            sheet.blit(draw_frame(index, facing),
                       (index * FRAME_W, row * FRAME_H))
    output = ROOT / "assets" / "sprites" / "npcs" / "cabin_light_entity.png"
    pygame.image.save(sheet, output)
    print(f"Wrote {output} ({sheet.get_width()}x{sheet.get_height()})")
    pygame.quit()


if __name__ == "__main__":
    main()
