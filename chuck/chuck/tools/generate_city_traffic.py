"""Generate four top-down modern cars for deterministic city traffic."""

import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame


ROOT = Path(__file__).resolve().parents[1]
FRAME_W = 40
FRAME_H = 20
COLOURS = (
    ((128, 42, 48), (178, 61, 65)),
    ((42, 75, 103), (63, 106, 139)),
    ((119, 104, 54), (164, 142, 70)),
    ((66, 70, 78), (101, 106, 115)),
)


def draw_car(surface: pygame.Surface, variant: int) -> None:
    dark, body = COLOURS[variant]
    # Wet road shadow and a long modern body seen from above/three-quarters.
    pygame.draw.ellipse(surface, (15, 18, 23, 150), (2, 4, 36, 15))
    pygame.draw.polygon(
        surface, dark,
        ((2, 7), (7, 3), (31, 3), (38, 7), (38, 15), (32, 18),
         (7, 18), (2, 14)),
    )
    pygame.draw.rect(surface, body, (5, 4, 29, 12))
    pygame.draw.polygon(
        surface, (49, 75, 91),
        ((13, 5), (29, 5), (32, 8), (11, 8)),
    )
    pygame.draw.polygon(
        surface, (35, 52, 66),
        ((11, 10), (32, 10), (29, 15), (13, 15)),
    )
    pygame.draw.line(surface, (199, 210, 207), (34, 7), (37, 8), 2)
    pygame.draw.line(surface, (142, 35, 34), (3, 8), (5, 8), 2)
    for x in (9, 30):
        pygame.draw.rect(surface, (19, 21, 25), (x, 1, 5, 3))
        pygame.draw.rect(surface, (19, 21, 25), (x, 16, 5, 3))
    pygame.draw.line(surface, (218, 224, 217), (7, 4), (31, 4))


def main() -> None:
    pygame.init()
    sheet = pygame.Surface((FRAME_W * len(COLOURS), FRAME_H), pygame.SRCALPHA)
    for variant in range(len(COLOURS)):
        frame = pygame.Surface((FRAME_W, FRAME_H), pygame.SRCALPHA)
        draw_car(frame, variant)
        sheet.blit(frame, (variant * FRAME_W, 0))
    output = ROOT / "assets" / "sprites" / "hazards" / "city_traffic.png"
    pygame.image.save(sheet, output)
    print(f"Wrote {output} ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
