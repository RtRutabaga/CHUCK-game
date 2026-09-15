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


def orc_frame(facing: str, weapon: str = "axe") -> Image.Image:
    """Phase 13's desert orc.

    Built to the same silhouette as the zombie so the two read as the
    same threat at a glance, and coloured against it so they never read
    as the same creature: the zombie is a sick green in rotted cloth,
    the orc is a harder grey-green in leather and sun-bleached wrap,
    with a heavy jaw and a shoulder line the zombie does not have.

    It stands upright, too. The zombie's giveaway is that one arm hangs
    forward and its tunic is torn open; nothing on the orc is falling
    apart, because nothing about it is dead.

    ...and it carries a battle axe, which is the loudest of those tells
    by a distance. Colour and jaw are read at four pixels; a shape held
    out past the silhouette is read across a room.
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

    if weapon == "bow":
        _longbow(draw, facing)
    else:
        _battle_axe(draw, facing)
    return image


def orc_archer_frame(facing: str) -> Image.Image:
    """The final encounter's orc archers: the same orc, with a bow.

    A quiver across the back and a bow held out ahead instead of the
    axe. Everything else is the orc Chuck has been walking past since
    the camp, because these are the same orcs -- the ones standing off
    and shooting rather than the ones charging in.
    """
    return orc_frame(facing, weapon="bow")


def _longbow(draw, facing: str) -> None:
    """A dark recurve held out past the silhouette, and a quiver."""
    wood = (70, 46, 28, 255)
    wood_lit = (112, 78, 44, 255)
    string = (206, 200, 176, 255)
    quiver = (110, 72, 40, 255)
    fletch = (178, 58, 44, 255)

    if facing == "up":
        # From behind: the quiver is the thing you see, and the bow is
        # out beside him.
        draw.rectangle((9, 9, 11, 19), fill=quiver)
        draw.point((9, 8), fill=fletch)
        draw.point((11, 7), fill=fletch)
        draw.line((1, 10, 0, 16), fill=wood, width=1)
        draw.line((0, 16, 1, 22), fill=wood, width=1)
        return
    if facing == "left":
        # In profile the bow is held out ahead, string toward him.
        draw.rectangle((11, 8, 13, 17), fill=quiver)
        draw.point((12, 7), fill=fletch)
        draw.point((13, 6), fill=fletch)
        draw.line((1, 9, 0, 15), fill=wood_lit, width=1)
        draw.line((0, 15, 1, 22), fill=wood_lit, width=1)
        draw.point((2, 8), fill=wood)
        draw.point((2, 23), fill=wood)
        draw.line((2, 9, 2, 22), fill=string, width=1)
        return
    # Facing the camera: the bow held across the body in the left hand,
    # the quiver's fletching over the right shoulder.
    draw.point((12, 9), fill=fletch)
    draw.point((13, 8), fill=fletch)
    draw.line((12, 10, 13, 9), fill=quiver, width=1)
    draw.line((15, 10, 15, 22), fill=wood, width=1)
    draw.point((14, 9), fill=wood_lit)
    draw.point((14, 23), fill=wood_lit)
    draw.line((13, 10, 13, 22), fill=string, width=1)


def _battle_axe(draw, facing: str) -> None:
    """The orc's axe, carried across the body.

    It is drawn last, over everything, because a weapon behind the arm
    holding it is a weapon nobody can see -- and being seen is the
    whole job. The orc was previously distinguished from the zombie by
    its colour and its jaw, which are both four pixels of information;
    a shape held out past the silhouette is legible from across a room.

    Sixteen pixels of width is not much to hang an axe on, so the haft
    runs corner to corner rather than upright. Held vertically the head
    lands on top of the orc's own head and the two shapes merge into a
    hat, which is the failure the knight's crest line already found
    once.
    """
    haft = (86, 58, 34, 255)
    haft_lit = (124, 90, 52, 255)
    steel = (176, 182, 190, 255)
    steel_lit = (222, 228, 236, 255)
    steel_dark = (92, 98, 108, 255)

    if facing == "up":
        # Over the far shoulder, so the back view is not the front view
        # with the face rubbed out.
        butt, head_x, blade = (11, 28), 3, (0, 4)
    elif facing == "left":
        # In profile it is carried ahead of him, edge first: an orc
        # walking toward you behind its own axe.
        butt, head_x, blade = (10, 27), 2, (0, 3)
    else:
        butt, head_x, blade = (4, 28), 12, (11, 15)

    # The haft: two pixels thick, with the light down one side of it.
    draw.line((butt[0], butt[1], head_x, 13), fill=haft, width=2)
    draw.line((butt[0], butt[1] - 1, head_x, 12), fill=haft_lit, width=1)

    # The head, at chest height rather than up beside the face. Carried
    # any higher it lands level with the orc's own head and the two
    # merge into one lumpy silhouette -- which is the same failure the
    # knight's crest found, one sprite over.
    #
    # Which way it faces is decided here rather than baked into the
    # shape, because the head is on the left in two facings and the
    # right in the third. Drawn one way round for all three, the two
    # left-handed ones had the bright cutting edge against the orc's
    # chest and the blunt back of the axe out at the frame edge -- the
    # only part of it the player can see, showing the wrong side.
    left, right = blade
    # Away from the butt of the haft, which is the only thing that
    # says which side of the orc the head is on.
    outward, inward = (left, right) if butt[0] > head_x else (right, left)
    draw.polygon(((inward, 7), (outward, 5), (outward, 16), (inward, 14)),
                 fill=steel)
    draw.line((outward, 5, outward, 16), fill=steel_lit)
    draw.line((inward, 7, inward, 14), fill=steel_dark)
    # The socket the haft passes through, so the head is mounted on it
    # rather than floating beside it. Between the haft and the *inner*
    # edge: laid across the whole head it painted out the blade.
    draw.rectangle((min(head_x, inward) - 1, 10, max(head_x, inward) + 1, 13),
                   fill=steel_dark)


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
                             ("orc_archer", orc_archer_frame),
                             ("knight", knight_frame)):
        sheet = Image.new("RGBA", (FRAME_W * 3, FRAME_H), (0, 0, 0, 0))
        for index, facing in enumerate(("down", "up", "left")):
            sheet.alpha_composite(make_frame(facing), (index * FRAME_W, 0))
        out = out_dir / f"{kind}.png"
        sheet.save(out)
        print(f"Wrote {out}")


if __name__ == "__main__":
    main()
