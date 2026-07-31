"""Feywild vegetation: Chult's silhouettes, plus one ordinary oak.

Phase 9's maps were reading blocky because their dense vegetation was
mostly bare tiles. Chult solved the same problem with rounded, pointed
tree and shrub props layered over the dense ground, so this reuses that
exact artwork -- same wild, un-blocky silhouettes -- and washes it with a
SUBTLE purple highlight so it belongs to the Feywild without becoming
psychedelic.

It also draws one genuinely ordinary oak. The Feywild already has glowing
spiral trees; a plain, believable tree keeps the region from turning into
visual noise, and gives the eye somewhere to rest.
"""

from pathlib import Path

from PIL import Image, ImageDraw

from generate_chult_props import jungle_shrub, jungle_tree

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sprites" / "objects"

# The Feywild highlight: violet is added ONLY where the light already
# falls, and the green channel is left alone, so the foliage keeps Chult's
# readable green mass and merely catches a strange sheen.
HIGHLIGHT_FLOOR = 70.0    # below this luma the pixel is untouched
RED_LIFT = 0.22
BLUE_LIFT = 0.46
SPARK = (198, 156, 236, 255)


def _feywild_wash(image: Image.Image, seed: int) -> Image.Image:
    """Add a subtle violet sheen to an existing Chult prop's lit faces."""
    out = image.copy()
    pixels = out.load()
    width, height = out.size
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a == 0:
                continue
            luma = (r * 2 + g * 3 + b) / 6
            if luma <= HIGHLIGHT_FLOOR:
                continue  # the shadowed mass stays pure Chult
            # Ramp in over the lit range only, and never touch green: the
            # leaves read green-with-a-violet-sheen, not purple.
            lit = min(1.0, (luma - HIGHLIGHT_FLOOR) / 90.0)
            pixels[x, y] = (
                min(255, round(r + (255 - r) * RED_LIFT * lit)),
                g,
                min(255, round(b + (255 - b) * BLUE_LIFT * lit)),
                a,
            )
    # A few motes caught in the canopy: the only overt magic on these.
    draw = ImageDraw.Draw(out)
    for index in range(3):
        x = (seed * 7 + index * 11) % max(1, width - 4) + 2
        y = (seed * 5 + index * 9) % max(1, height // 2) + 2
        if pixels[x, y][3] > 0:
            draw.point((x, y), fill=SPARK)
    return out


def feywild_oak(variant: int) -> Image.Image:
    """A plain oak: brown bark, green crown, no glow and no strangeness.

    Deliberately the most ordinary thing in the Feywild."""
    image = Image.new("RGBA", (36, 50), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    shadow = (28, 36, 30, 175)
    bark_dark = (58, 42, 30, 255)
    bark = (86, 63, 42, 255)
    bark_light = (114, 86, 58, 255)
    leaf_dark = (30, 62, 36, 255)
    leaf_mid = (44, 86, 46, 255)
    leaf = (62, 110, 56, 255)
    leaf_light = (88, 134, 68, 255)

    lean = (-1, 0, 1)[variant]
    cx = 18 + lean
    draw.ellipse((8, 44, 29, 49), fill=shadow)

    # A stout, slightly flared oak trunk with two low boughs.
    draw.polygon(((13, 47), (23, 47), (21 + lean, 24), (15 + lean, 24)),
                 fill=bark_dark)
    draw.polygon(((15, 46), (21, 46), (20 + lean, 25), (16 + lean, 25)),
                 fill=bark)
    draw.line((18, 44, 18 + lean, 27), fill=bark_light)
    draw.line((16 + lean, 30, 10 + lean, 24), fill=bark_dark, width=2)
    draw.line((20 + lean, 32, 26 + lean, 26), fill=bark_dark, width=2)

    # A broad, rounded oak crown: overlapping lobes, densest at the core.
    lobes = (
        (-15, -6, 16, 15), (-6, -12, 17, 16), (3, -7, 15, 15),
        (-12, 3, 15, 13), (0, 4, 16, 13), (-5, -2, 16, 14),
    )
    for index, (dx, dy, w, h) in enumerate(lobes):
        x = cx + dx + ((index + variant) % 3 - 1)
        y = 20 + dy
        shade = (leaf_dark if index < 2
                 else leaf_mid if index < 4 else leaf)
        draw.ellipse((x, y, x + w, y + h), fill=shade)
    # Sunlit crest and a few leaf clusters breaking the outline.
    for dx, dy, w, h in ((-8, -10, 11, 8), (1, -8, 10, 7), (-4, 0, 12, 8)):
        draw.ellipse((cx + dx, 20 + dy, cx + dx + w, 20 + dy + h),
                     fill=leaf_light)
    for dx, dy in ((-16, 2), (14, -2), (-10, -13), (9, 10), (-13, 9)):
        x, y = cx + dx, 20 + dy
        draw.ellipse((x - 3, y - 3, x + 3, y + 3),
                     fill=leaf_mid if (dx + dy) % 2 else leaf)
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    written = []
    for variant in range(3):
        # Chult's tree and shrub, worn Feywild-violet.
        grove = _feywild_wash(jungle_tree(variant), seed=variant + 1)
        grove.save(OUT / f"feywild_grove_tree_{variant + 1}.png")
        shrub = _feywild_wash(jungle_shrub(variant), seed=variant + 4)
        shrub.save(OUT / f"feywild_shrub_{variant + 1}.png")
        feywild_oak(variant).save(OUT / f"feywild_oak_{variant + 1}.png")
        written += [f"feywild_grove_tree_{variant + 1}",
                    f"feywild_shrub_{variant + 1}",
                    f"feywild_oak_{variant + 1}"]
    for name in written:
        print(f"Wrote {OUT / (name + '.png')}")


if __name__ == "__main__":
    main()
