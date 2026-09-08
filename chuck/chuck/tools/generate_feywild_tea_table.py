"""Author Feywild 5: the enemy-free Giant Tea Table exploration respite."""

from collections import deque
from pathlib import Path

try:
    from tools.feywild_mushroom_dressing import dress_grid
except ModuleNotFoundError:  # Direct execution from inside tools/.
    from feywild_mushroom_dressing import dress_grid


W, H = 72, 52
OUT = (
    Path(__file__).resolve().parents[1]
    / "assets" / "maps" / "feywild_tea_table.txt"
)

RETURN_EXIT = (12, 0)
ARRIVAL = (12, 1)
ANCHOR = (17, 5)
FUTURE_RETURN = (60, 50)
FUTURE_EXIT = (60, 51)
CACHE_DOOR = (14, 27)
CACHE = (10, 27)

HEADER = [
    "; PHASE 9 - FEYWILD 5, THE GIANT TEA TABLE (72x52 tiles).",
    "; An abandoned Fey place setting becomes architecture to one-foot Chuck.",
    "; The required route passes beneath the table; there are no enemies.",
    "; One physical Ashtray serves the map; Map 6 remains an inert boundary.",
]


def _room(
    grid: list[list[str]],
    left: int,
    top: int,
    right: int,
    bottom: int,
    char: str = ".",
) -> None:
    for row in range(top, bottom + 1):
        for col in range(left, right + 1):
            grid[row][col] = char


def _root_cache(grid: list[list[str]]) -> None:
    left, top, right, bottom = 6, 23, 14, 31
    for col in range(left, right + 1):
        grid[top][col] = "※"
        grid[bottom][col] = "※"
    for row in range(top, bottom + 1):
        grid[row][left] = "※"
        grid[row][right] = "※"
    _room(grid, left + 1, top + 1, right - 1, bottom - 1, "'")
    grid[CACHE_DOOR[1]][CACHE_DOOR[0]] = "≀"
    grid[CACHE[1]][CACHE[0]] = "<"


def build() -> list[list[str]]:
    grid = [["#"] * W for _ in range(H)]

    # Broad rooms above and below the gathering are connected by the table's
    # sheltered underside. Side aisles end at the front hedge, so progression
    # uses Chuck's scale rather than merely walking around the furniture.
    _room(grid, 5, 1, 66, 11)
    _room(grid, 5, 10, 17, 37)
    _room(grid, 56, 10, 66, 37)
    _room(grid, 10, 39, 66, 50)

    # The tabletop is an enormous solid field. Its place settings are authored
    # directly on it, while the cool shadow below is traversable architecture.
    _room(grid, 18, 12, 55, 28, "▤")
    _room(grid, 18, 29, 55, 38, "░")

    # Heavy overhead aprons frame every way into or out of the under-table
    # route. Large actors treat both apron and shadow as solid terrain.
    # There is no lip round the shadow any more. There was a wooden one,
    # a beam drawn across the top of every tile of the ring, and from
    # above at this distance a thin frame around a dark rectangle is a
    # picture frame rather than the edge of a table. What says "under
    # the table" is the shadow, and it says it without help.
    #
    # Nothing about the scale gate depended on the frame either. The
    # shadow was already the tile too low for anything bigger than
    # Chuck, so taking the frame off changes how the table looks and
    # nothing at all about who can get under it.

    # Two legs, and both of them up against the table.
    #
    # There were four, a near pair and a far pair in the same columns.
    # Legs are seventy pixels of sprite drawn upward from the bottom of
    # their tile, so a pair four rows apart stacks into one hundred and
    # thirty-four pixels of continuous post with a joint halfway up it --
    # which is not a table with four legs, it is a pillar.
    #
    # Row 32 is the row where a leg's top meets the underside of the
    # tabletop and overlaps it by a few pixels, so the leg is holding
    # the table up. Standing any further down it is a post with a gap
    # above it, which is a leg holding nothing.
    for col, row in ((21, 32), (52, 32)):
        grid[row][col] = "♜"

    # Nothing stands loose in the western aisle any more either. Three
    # chair legs were scattered there, each on its own in open ground
    # with no seat over it and no second leg near enough to belong to
    # the same chair, so what they read as was fence posts nobody built
    # a fence out of. The freestanding legs east of the table were cut
    # for exactly this reason and these are the same object.

    # Two complete place settings and the remnants of another gathering.
    for col, row in ((27, 18), (45, 18), (44, 28)):
        grid[row][col] = "◉"
    for col, row in ((31, 22), (49, 22), (30, 28)):
        grid[row][col] = "☕"
    for col, row in ((22, 24), (41, 24), (52, 16)):
        grid[row][col] = "⌁"
    for col, row in (
        (24, 15), (35, 17), (39, 21), (48, 26), (25, 27), (52, 12),
    ):
        grid[row][col] = "⁙"
    for col, row in ((34, 24), (36, 24), (37, 25), (50, 15)):
        grid[row][col] = "◍"

    # A root pocket off the western aisle offers one entirely scale-gated
    # cache. Ordinary breakable vegetation recurs in the quiet southern room.
    _root_cache(grid)
    for col, row in ((14, 43), (39, 46), (63, 43)):
        grid[row][col] = "<"

    # Dense enchanted islands keep the lower room exploratory rather than a
    # straight walk to the future edge.
    for left, top, right, bottom in (
        (22, 40, 29, 44),
        (46, 44, 54, 49),
        (58, 39, 65, 41),
    ):
        _room(grid, left, top, right, bottom, "#")
    for col, row, char in (
        (24, 42, "ł"), (49, 46, "ł"), (61, 40, "ł"),
        (16, 47, "Ł"), (34, 42, "ŋ"), (57, 47, "ŋ"),
        (8, 8, "Ł"), (62, 7, "ŋ"),
    ):
        if grid[row][col] in {".", "#"}:
            grid[row][col] = char

    # Chult-style three-cell handoffs occupy actual outer edges.
    for col in range(RETURN_EXIT[0] - 1, RETURN_EXIT[0] + 2):
        grid[0][col] = "⇧"
    grid[ARRIVAL[1]][ARRIVAL[0]] = "Պ"
    grid[ANCHOR[1]][ANCHOR[0]] = "Ջ"
    grid[FUTURE_RETURN[1]][FUTURE_RETURN[0]] = "Ս"
    for col in range(FUTURE_EXIT[0] - 1, FUTURE_EXIT[0] + 2):
        grid[H - 1][col] = "⇩"
    grid[FUTURE_EXIT[1]][FUTURE_EXIT[0]] = "Ռ"
    _dress_with_vegetation(grid)
    dress_grid("feywild_tea_table", grid)
    return grid


def _dress_with_vegetation(grid: list[list[str]]) -> None:
    """The region's wood, standing on the dense growth it breaks up.

    Every other Feywild map grows its trees here, in its own generator,
    from its own reading of where the mass is thick. This map's were put
    straight into the shipped text file and never written down anywhere
    else, so the generator did not reproduce the map it ships: running
    it dropped a hundred and eighty trees and left the dense blocks
    reading as flat green slabs again. It is written down now, where it
    can be run twice and come out the same both times.

    Only tiles that are already dense growth with growth on three sides
    are dressed, so this replaces solid with solid and leaves every
    route exactly as it was -- which is what let the original pass claim
    solidity was unchanged byte for byte.
    """
    height, width = len(grid), len(grid[0])
    # Every tile that could take a tree is found before any of them is
    # planted. Planting as we go was the first version, and it eats its
    # own map: a tile dressed on this row is no longer dense growth for
    # the neighbour test on the next one, so the mass shrinks ahead of
    # the sweep and the last kind placed gets a tenth of what it should.
    thick = [
        (col, row)
        for row in range(1, height - 1)
        for col in range(1, width - 1)
        if grid[row][col] == "#"
        and sum(
            grid[row + drow][col + dcol] == "#"
            for dcol, drow in ((1, 0), (-1, 0), (0, 1), (0, -1))
        ) >= 3
    ]
    for col, row in thick:
        key = (col * 31 + row * 17) % 7
        if key == 0:
            grid[row][col] = "ŧ"
        elif key == 3:
            grid[row][col] = "Ŧ"
        elif key == 5 and (col * 5 + row * 3) % 17 == 0:
            # The plain oak stays a landmark rather than a third kind of
            # tree: one in seventeen of the tiles that could take one,
            # which on this map is a handful.
            grid[row][col] = "Ɓ"


def _under(char: str) -> str:
    return {
        "Պ": ".", "Ջ": ".", "Ռ": "⇩", "Ս": ".",
        "<": ".", "♜": "░",
        "◉": "▤", "☕": "▤", "⌁": "▤", "⁙": "▤",
    }.get(char, char)


def _reachable(
    grid: list[list[str]],
    start: tuple[int, int],
    *,
    large_actor: bool = False,
) -> set[tuple[int, int]]:
    blocked = {"#", "▤", "◍", "※", "♜", "◉", "☕", "⌁", "⁙",
               "ł", "Ł", "ŋ", "ŧ", "Ŧ", "Ɓ"}
    reached = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for point in (
            (col - 1, row), (col + 1, row),
            (col, row - 1), (col, row + 1),
        ):
            x, y = point
            if not (0 <= x < W and 0 <= y < H) or point in reached:
                continue
            terrain = _under(grid[y][x])
            if terrain in blocked:
                continue
            if large_actor and terrain in {"≀", "░"}:
                continue
            reached.add(point)
            frontier.append(point)
    return reached


def validate(grid: list[list[str]]) -> None:
    assert len(grid) == H and all(len(row) == W for row in grid)
    chuck_reach = _reachable(grid, ARRIVAL)
    assert {
        RETURN_EXIT, ANCHOR, FUTURE_RETURN, FUTURE_EXIT,
        CACHE_DOOR, CACHE,
    } <= chuck_reach
    large_reach = _reachable(grid, ARRIVAL, large_actor=True)
    assert FUTURE_EXIT not in large_reach
    assert CACHE not in large_reach
    text = "".join("".join(row) for row in grid)
    assert text.count("Ջ") == 1
    assert text.count("<") == 4
    assert text.count("♜") == 2
    assert "♧" not in text
    # The shadow is one unbroken field with nothing framing it.
    assert all(
        grid[row][col] in {"░", "♜"}
        for row in range(29, 39) for col in range(18, 56)
    )
    # The wood, at the counts the region's own suite asks of every
    # Feywild map. Derived from the pass above rather than pinned to it,
    # so this says "dressed" and not "dressed exactly like this".
    assert text.count("ŧ") >= 20
    assert text.count("Ŧ") >= 15
    assert 0 < text.count("Ɓ") <= text.count("ŧ")
    assert text.count("◉") == 3 and text.count("☕") == 3
    assert all(grid[0][col] == "⇧" for col in range(11, 14))
    assert all(
        grid[H - 1][col] in {"⇩", "Ռ"} for col in range(59, 62)
    )


def main() -> None:
    grid = build()
    validate(grid)
    OUT.write_text(
        "\n".join(HEADER + ["".join(row) for row in grid]) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
