"""Author Feywild 13: the Twilight Crossroads.

The final Phase 9 map is a broad clearing whose routes look ordinary but
connect wrongly: the Luminous Rapids' east bank arrives from the south, while
the eventual wizard-tower route waits at the west edge.  One flower exchanges
an open northern decoy for the actual western way onward.  Pollen offers a
short direct route through the clearing, and a root pocket gives Chuck a
small-scale optional refuge and cache.

The western boundary is intentionally inert.  A later phase may connect it,
but this pass stops at a stable, readable wilderness opening.
"""

from collections import deque
from pathlib import Path

try:
    from tools.feywild_mushroom_dressing import dress_grid
except ModuleNotFoundError:  # Direct execution from inside tools/.
    from feywild_mushroom_dressing import dress_grid


W, H = 76, 52
OUT = (
    Path(__file__).resolve().parents[1]
    / "assets" / "maps" / "feywild_twilight_crossroads.txt"
)

RETURN_EXIT = (38, 51)
ARRIVAL = (38, 50)
ANCHOR = (38, 44)
TOWER_EXIT = (0, 14)
TOWER_RETURN = (1, 14)
SWITCH = (20, 17)
OPENS = tuple((13, row) for row in range(13, 16))
CLOSES = tuple((col, 9) for col in range(36, 39))
ROOT_PASSAGES = ((58, 13), (65, 18))

# Marker characters are deliberately map-local.  Ordinary enemies reuse the
# shared Phase 9 markers because their behaviour is not map-specific.
MARKERS = {
    "switch": "Ꭰ",
    "open": "Ꭱ",
    "close": "Ꭲ",
    "arrival": "Ꭳ",
    "anchor": "Ꭴ",
    "tower": "Ꭵ",
    "tower_return": "Ꭶ",
}
THORN_MITE = "\u10e6"
REDCAP = "զ"

MITES = ((25, 28), (46, 25), (53, 36), (22, 39), (51, 18))
REDCAP_POS = (66, 27)
CACHES = ((64, 11), (69, 15), (57, 40))

HEADER = [
    "; PHASE 9 - FEYWILD 13, THE TWILIGHT CROSSROADS (76x52 tiles).",
    "; The Rapids' eastward route arrives here from the south. Ordinary",
    "; trails branch toward false horizons, while one reciprocal flower",
    "; opens the west route and closes the north decoy. The final western",
    "; wilderness opening is a stable, inert boundary for the later tower.",
]


def _room(grid, left, top, right, bottom, char="."):
    for row in range(top, bottom + 1):
        for col in range(left, right + 1):
            grid[row][col] = char


def _path(grid, cells, radius=1):
    """Paint a three-tile authored trail along orthogonal segments."""
    for (x1, y1), (x2, y2) in zip(cells, cells[1:]):
        assert x1 == x2 or y1 == y2
        if x1 == x2:
            for row in range(min(y1, y2), max(y1, y2) + 1):
                for col in range(x1 - radius, x1 + radius + 1):
                    grid[row][col] = "'"
        else:
            for col in range(min(x1, x2), max(x1, x2) + 1):
                for row in range(y1 - radius, y1 + radius + 1):
                    grid[row][col] = "'"


def build() -> list[list[str]]:
    grid = [["#"] * W for _ in range(H)]

    # Broad central clearing, with an irregular edge instead of a rectangle.
    for row in range(18, 45):
        inset = max(0, abs(row - 31) - 8)
        left, right = 16 + inset, 59 - inset
        _room(grid, left, row, right, row)
    _room(grid, 21, 23, 66, 39)

    # Normal-looking trails lead in four directions. Geography is wrong on
    # purpose: the east edge of Map 12 reaches the southern trail here.
    _path(grid, [(38, 51), (38, 31)])
    _path(grid, [(37, 24), (37, 6)])       # northern decoy
    _path(grid, [(50, 27), (72, 27)])      # eastern dead end
    _path(grid, [(48, 39), (67, 39)])      # southeast loop
    _path(grid, [(22, 27), (22, 14), (14, 14)])

    # The eventual tower approach. Its edge opening reads like the Chult
    # wilderness exits, but the flower gate initially keeps it unreachable.
    _room(grid, 1, 10, 12, 18)
    _path(grid, [(1, 14), (12, 14)])

    # Root-walled optional pocket. Chuck slips through the one-tile passage;
    # the redcap outside is too large to follow him into the cache.
    _room(grid, 58, 7, 72, 18, "※")
    _room(grid, 59, 8, 71, 17)
    _path(grid, [(55, 26), (55, 13), (58, 13)])
    grid[12][58] = "※"
    grid[14][58] = "※"
    grid[13][58] = "≀"
    # A second low mouth rejoins the eastern path. The pocket is therefore a
    # real Chuck-sized shortcut, not merely a one-way cache alcove.
    _path(grid, [(65, 18), (65, 27)])
    grid[18][64] = "※"
    grid[18][66] = "※"
    grid[18][65] = "≀"

    # A direct pollen-heavy line through the clearing; the longer dry arc on
    # the east side remains available, so slowing pollen is a choice.
    for row in range(34, 42):
        for col in range(33, 44):
            if grid[row][col] not in {".", "'"}:
                continue
            if (col * 5 + row * 7) % 4 != 0:
                grid[row][col] = "☼"

    _dress_dense_edge(grid)

    # Flower exchange: open the west gate, close the harmless north decoy.
    grid[SWITCH[1]][SWITCH[0]] = MARKERS["switch"]
    for col, row in OPENS:
        assert grid[row][col] == "#"
        grid[row][col] = MARKERS["open"]
    for col, row in CLOSES:
        assert grid[row][col] == "'"
        grid[row][col] = MARKERS["close"]

    for col, row in MITES:
        assert grid[row][col] in {".", "'"}
        grid[row][col] = THORN_MITE
    grid[REDCAP_POS[1]][REDCAP_POS[0]] = REDCAP
    for col, row in CACHES:
        assert grid[row][col] in {".", "'"}
        grid[row][col] = "<"

    # Three-cell openings remain legible as wilderness gaps at native scale.
    for col in range(RETURN_EXIT[0] - 1, RETURN_EXIT[0] + 2):
        grid[H - 1][col] = "⇩"
    for row in range(TOWER_EXIT[1] - 1, TOWER_EXIT[1] + 2):
        grid[row][0] = "←"
    grid[ARRIVAL[1]][ARRIVAL[0]] = MARKERS["arrival"]
    grid[ANCHOR[1]][ANCHOR[0]] = MARKERS["anchor"]
    grid[TOWER_EXIT[1]][TOWER_EXIT[0]] = MARKERS["tower"]
    grid[TOWER_RETURN[1]][TOWER_RETURN[0]] = MARKERS["tower_return"]
    dress_grid("feywild_twilight_crossroads", grid)
    return grid


def _dress_dense_edge(grid) -> None:
    """Reuse the established dense-tree/shrub silhouettes at the margins."""
    for row in range(1, H - 1):
        for col in range(1, W - 1):
            if grid[row][col] != "#":
                continue
            neighbours = sum(
                grid[row + dr][col + dc] == "#"
                for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1))
            )
            if neighbours < 3:
                continue
            key = (col * 31 + row * 17) % 23
            if key == 0:
                grid[row][col] = "ŧ"
            elif key == 7:
                grid[row][col] = "Ŧ"
            elif key == 14:
                grid[row][col] = "Ɓ"


def _base(char: str) -> str:
    return {
        MARKERS["switch"]: ".",
        MARKERS["open"]: "#",
        MARKERS["close"]: "'",
        MARKERS["arrival"]: "'",
        MARKERS["anchor"]: ".",
        MARKERS["tower"]: "←",
        MARKERS["tower_return"]: "'",
        THORN_MITE: ".",
        REDCAP: ".",
        "<": ".",
    }.get(char, char)


def _reachable(grid, *, flower_active: bool) -> set[tuple[int, int]]:
    solid = {"#", "ŧ", "Ŧ", "Ɓ", "※", "ŋ"}
    open_tiles = set()
    for row in range(H):
        for col in range(W):
            terrain = _base(grid[row][col])
            if terrain not in solid:
                open_tiles.add((col, row))
    if flower_active:
        open_tiles |= set(OPENS)
        open_tiles -= set(CLOSES)
    reached = {ARRIVAL}
    frontier = deque([ARRIVAL])
    while frontier:
        col, row = frontier.popleft()
        for nxt in ((col - 1, row), (col + 1, row),
                    (col, row - 1), (col, row + 1)):
            if nxt in open_tiles and nxt not in reached:
                reached.add(nxt)
                frontier.append(nxt)
    return reached


def validate(grid) -> None:
    assert len(grid) == H and all(len(row) == W for row in grid)
    idle = _reachable(grid, flower_active=False)
    active = _reachable(grid, flower_active=True)
    assert SWITCH in idle and ANCHOR in idle and RETURN_EXIT in idle
    assert TOWER_EXIT not in idle, "tower route does not require the flower"
    assert TOWER_EXIT in active, "flower does not open the tower approach"
    assert set(ROOT_PASSAGES) <= idle and set(CACHES) <= active
    assert all(grid[H - 1][col] in {"⇩"}
               for col in range(RETURN_EXIT[0] - 1, RETURN_EXIT[0] + 2))
    assert all(grid[row][0] in {"←", MARKERS["tower"]}
               for row in range(TOWER_EXIT[1] - 1, TOWER_EXIT[1] + 2))
    text = "".join("".join(row) for row in grid)
    assert text.count(MARKERS["anchor"]) == 1
    assert text.count(THORN_MITE) == len(MITES)
    assert text.count(REDCAP) == 1
    assert text.count("☼") >= 50
    assert text.count("<") == len(CACHES)


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
