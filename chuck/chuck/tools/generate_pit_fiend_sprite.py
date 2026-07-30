"""Generate the human-towering Pit Fiend used in the Phase 8 battle."""

from pathlib import Path

from PIL import Image, ImageDraw


W, H = 48, 48


def main() -> None:
    image = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    shadow = (20, 15, 18, 170)
    outline = (30, 18, 24, 255)
    dark = (76, 25, 31, 255)
    body = (132, 42, 40, 255)
    light = (179, 65, 45, 255)
    wing = (64, 29, 43, 255)
    horn = (190, 151, 92, 255)
    eye = (255, 189, 46, 255)
    flame = (244, 103, 30, 255)

    draw.ellipse((5, 42, 43, 47), fill=shadow)
    # Wide bat wings make the fiend read at a glance above the trio.
    draw.polygon(((20, 14), (8, 5), (1, 9), (8, 23), (2, 31),
                  (18, 29)), fill=outline)
    draw.polygon(((28, 14), (40, 5), (47, 9), (40, 23), (46, 31),
                  (30, 29)), fill=outline)
    draw.polygon(((18, 16), (9, 9), (5, 11), (11, 21), (7, 27),
                  (19, 25)), fill=wing)
    draw.polygon(((30, 16), (39, 9), (43, 11), (37, 21), (41, 27),
                  (29, 25)), fill=wing)
    # Horns, head, huge torso, and digitigrade legs.
    draw.polygon(((18, 10), (13, 1), (20, 6)), fill=horn)
    draw.polygon(((30, 10), (35, 1), (28, 6)), fill=horn)
    draw.rectangle((17, 7, 31, 18), fill=outline)
    draw.rectangle((19, 8, 29, 17), fill=body)
    draw.rectangle((20, 11, 22, 13), fill=eye)
    draw.rectangle((27, 11, 29, 13), fill=eye)
    draw.polygon(((15, 17), (33, 17), (38, 31), (31, 38),
                  (17, 38), (10, 31)), fill=outline)
    draw.polygon(((17, 18), (31, 18), (34, 30), (29, 35),
                  (19, 35), (14, 30)), fill=body)
    draw.rectangle((20, 20, 28, 30), fill=light)
    draw.line((14, 20, 5, 31), fill=body, width=5)
    draw.line((34, 20, 42, 30), fill=body, width=5)
    draw.polygon(((19, 34), (14, 44), (22, 44), (25, 35)), fill=dark)
    draw.polygon(((29, 34), (34, 44), (26, 44), (23, 35)), fill=dark)
    # Barbed tail and a restrained lick of infernal heat at its tip.
    draw.line((31, 31, 42, 37, 45, 33), fill=outline, width=4)
    draw.polygon(((44, 34), (47, 28), (47, 37)), fill=flame)

    out = (Path(__file__).resolve().parents[1] /
           "assets" / "sprites" / "npcs" / "pit_fiend.png")
    # Author the silhouette at a tight scale, then enlarge with nearest
    # neighbor so the Pit Fiend towers over human NPCs without smoothing.
    image.resize((64, 64), Image.Resampling.NEAREST).save(out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
