"""Generate the human-scale pursuers: zombie, skeleton, orc, knight."""

from pathlib import Path

from PIL import Image, ImageDraw


FRAME_W, FRAME_H = 16, 30


def zombie_frame(facing: str) -> Image.Image:
    image = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    skin = (105, 126, 73, 255)
    shade = (63, 82, 53, 255)
    cloth = (66, 64, 55, 255)
    tear = (42, 44, 39, 255)
    draw.rectangle((4, 1, 11, 8), fill=shade)
    draw.rectangle((5, 2, 10, 8), fill=skin)
    if facing == "down":
        draw.point((6, 4), fill=(215, 205, 150, 255))
        draw.point((9, 4), fill=(215, 205, 150, 255))
    elif facing == "left":
        draw.point((5, 4), fill=(215, 205, 150, 255))
    draw.rectangle((3, 9, 12, 21), fill=cloth)
    draw.rectangle((4, 15, 7, 18), fill=tear)
    arm_shift = 0 if facing != "left" else -2
    draw.rectangle((1 + arm_shift, 10, 3 + arm_shift, 23), fill=skin)
    draw.rectangle((12, 11, 14, 22), fill=skin)
    draw.rectangle((4, 22, 7, 29), fill=shade)
    draw.rectangle((9, 22, 12, 29), fill=shade)
    return image


def skeleton_frame(facing: str) -> Image.Image:
    image = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    bone = (202, 199, 166, 255)
    light = (232, 226, 190, 255)
    dark = (40, 46, 38, 255)
    draw.rectangle((4, 1, 11, 8), fill=bone)
    draw.rectangle((5, 2, 10, 7), fill=light)
    if facing == "down":
        draw.rectangle((5, 4, 6, 5), fill=dark)
        draw.rectangle((9, 4, 10, 5), fill=dark)
    elif facing == "left":
        draw.rectangle((4, 4, 5, 5), fill=dark)
    draw.rectangle((7, 9, 8, 21), fill=bone)
    for y in (11, 14, 17):
        draw.line((3, y, 12, y), fill=bone, width=2)
    draw.line((3, 10, 1, 22), fill=bone, width=2)
    draw.line((12, 10, 14, 22), fill=bone, width=2)
    draw.line((7, 21, 4, 29), fill=bone, width=2)
    draw.line((8, 21, 11, 29), fill=bone, width=2)
    return image


def orc_frame(facing: str) -> Image.Image:
    """Phase 13's desert orc.

    Built to the same silhouette as the zombie so the two read as the
    same threat at a glance, and coloured against it so they never read
    as the same creature: the zombie is a sick green in rotted cloth,
    the orc is a harder grey-green in leather and sun-bleached wrap,
    with a heavy jaw and a shoulder line the zombie does not have.

    It stands upright, too. The zombie's giveaway is that one arm hangs
    forward and its tunic is torn open; nothing on the orc is falling
    apart, because nothing about it is dead.
    """
    image = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    skin = (96, 116, 88, 255)
    shade = (62, 78, 60, 255)
    jaw = (120, 138, 104, 255)
    leather = (92, 66, 42, 255)
    strap = (58, 42, 28, 255)
    wrap = (176, 162, 128, 255)
    tusk = (232, 228, 198, 255)

    # Head, with the jaw carried forward: the one shape that separates
    # it from the zombie at sixteen pixels wide.
    draw.rectangle((4, 1, 11, 8), fill=shade)
    draw.rectangle((5, 2, 10, 7), fill=skin)
    draw.rectangle((5, 6, 10, 8), fill=jaw)
    if facing == "down":
        draw.point((6, 4), fill=(226, 196, 96, 255))
        draw.point((9, 4), fill=(226, 196, 96, 255))
        draw.point((6, 8), fill=tusk)
        draw.point((9, 8), fill=tusk)
    elif facing == "left":
        draw.point((5, 4), fill=(226, 196, 96, 255))
        draw.point((4, 8), fill=tusk)

    # Shoulders wider than the body below them. The dark line sits low
    # on the chest rather than up under the jaw: drawn across the top of
    # the shoulders it read as the brim of a hat.
    draw.rectangle((2, 10, 13, 13), fill=leather)
    draw.rectangle((3, 14, 12, 21), fill=wrap)
    draw.line((3, 16, 12, 18), fill=strap, width=1)

    arm_shift = 0 if facing != "left" else -1
    draw.rectangle((1 + arm_shift, 11, 3 + arm_shift, 21), fill=skin)
    draw.rectangle((12, 11, 14, 21), fill=skin)
    # A dark edge down the outside of each arm, or the arms disappear
    # into shoulders the same colour and it reads as one wide block.
    draw.line((1 + arm_shift, 11, 1 + arm_shift, 21), fill=shade)
    draw.line((14, 11, 14, 21), fill=shade)
    # Bracers, because a thing that carries no weapon still has to look
    # like it came here to fight.
    draw.rectangle((1 + arm_shift, 18, 3 + arm_shift, 20), fill=leather)
    draw.rectangle((12, 18, 14, 20), fill=leather)

    draw.rectangle((4, 22, 7, 29), fill=shade)
    draw.rectangle((9, 22, 12, 29), fill=shade)
    draw.rectangle((4, 26, 7, 29), fill=leather)
    draw.rectangle((9, 26, 12, 29), fill=leather)
    return image


def knight_frame(facing: str) -> Image.Image:
    """Phase 13's armoured knight, out of the medieval fragment.

    The only one of these four with no skin showing. Every other
    pursuer in the game is read by its face -- the zombie's sick green,
    the skeleton's skull, the orc's jaw -- and this one is read by not
    having one: a helm with a slit in it, and plate everywhere else.

    Broader at the shoulders than the orc and narrower at the waist,
    which is the silhouette of a breastplate rather than a body.
    """
    image = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    steel = (146, 150, 158, 255)
    steel_lit = (196, 200, 208, 255)
    steel_dark = (78, 82, 92, 255)
    dark = (34, 36, 42, 255)
    surcoat = (122, 46, 52, 255)

    # Helm: a plain barrel with a slit, and a crest ridge over it.
    draw.rectangle((4, 1, 11, 9), fill=steel_dark)
    draw.rectangle((5, 2, 10, 8), fill=steel)
    draw.line((7, 0, 8, 0), fill=steel_lit)
    draw.line((5, 2, 10, 2), fill=steel_lit)
    if facing == "down":
        draw.rectangle((6, 5, 9, 6), fill=dark)
        draw.point((7, 8), fill=dark)
        draw.point((8, 8), fill=dark)
    elif facing == "left":
        draw.rectangle((4, 5, 6, 6), fill=dark)

    # Pauldrons wider than the chest under them.
    draw.rectangle((1, 10, 14, 13), fill=steel_dark)
    draw.rectangle((2, 10, 13, 12), fill=steel)
    draw.line((2, 10, 13, 10), fill=steel_lit)
    # Breastplate, tapering to the waist, with a surcoat down it.
    draw.rectangle((3, 13, 12, 18), fill=steel)
    draw.rectangle((4, 19, 11, 22), fill=steel_dark)
    draw.rectangle((7, 13, 8, 21), fill=surcoat)
    draw.line((3, 14, 12, 14), fill=steel_lit)

    arm_shift = 0 if facing != "left" else -1
    draw.rectangle((1 + arm_shift, 13, 3 + arm_shift, 21), fill=steel_dark)
    draw.rectangle((12, 13, 14, 21), fill=steel_dark)
    draw.line((1 + arm_shift, 13, 1 + arm_shift, 21), fill=dark)
    draw.line((14, 13, 14, 21), fill=dark)

    # Greaves and sabatons: plate all the way down.
    draw.rectangle((4, 22, 7, 29), fill=steel)
    draw.rectangle((9, 22, 12, 29), fill=steel)
    draw.rectangle((4, 27, 7, 29), fill=steel_dark)
    draw.rectangle((9, 27, 12, 29), fill=steel_dark)
    return image


def main() -> None:
    out_dir = Path(__file__).resolve().parents[1] / "assets" / "sprites" / "hazards"
    out_dir.mkdir(parents=True, exist_ok=True)
    for kind, make_frame in (("zombie", zombie_frame),
                             ("skeleton", skeleton_frame),
                             ("orc", orc_frame),
                             ("knight", knight_frame)):
        sheet = Image.new("RGBA", (FRAME_W * 3, FRAME_H), (0, 0, 0, 0))
        for index, facing in enumerate(("down", "up", "left")):
            sheet.alpha_composite(make_frame(facing), (index * FRAME_W, 0))
        out = out_dir / f"{kind}.png"
        sheet.save(out)
        print(f"Wrote {out}")


if __name__ == "__main__":
    main()
