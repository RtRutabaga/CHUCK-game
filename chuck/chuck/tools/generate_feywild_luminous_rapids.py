"""Author Feywild 12: the Luminous Rapids, where the region adds up.

Three crossings of a bright impassable river, in teaching order. The
first is static stones and one-tile jumps, exactly as the Moonmoth Fen
taught them. The second and third are twin chains of giant lily pads
where a reactive flower raises one chain and sinks the other, so the
question stops being "can I make this jump" and becomes "which crossing
do I want to exist right now".

Pollen thickens the approaches and never a landing tile; lantern moths
patrol the lanes; the one spitting orchid sits on the optional ledge.

The validator walks the whole (tile, group-state) space with the jump
rule built in, and proves the same three things the Shifting Hedge does:
the exit is reachable, it is not reachable by walking alone, and from
every state Chuck can reach, the exit is still reachable.
"""

from collections import deque
from itertools import product
from pathlib import Path

try:
    from tools.feywild_mushroom_dressing import dress_grid
except ModuleNotFoundError:  # Direct execution from inside tools/.
    from feywild_mushroom_dressing import dress_grid
try:
    from tools.feywild_great_tree_dressing import (
        dress_grid as plant_great_tree,
    )
except ModuleNotFoundError:  # Direct execution from inside tools/.
    from feywild_great_tree_dressing import dress_grid as plant_great_tree

W, H = 78, 44
OUT = (
    Path(__file__).resolve().parents[1]
    / "assets" / "maps" / "feywild_luminous_rapids.txt"
)

RETURN_EXIT = (0, 21)
ARRIVAL = (1, 21)
ANCHOR = (33, 21)
FUTURE_RETURN = (76, 21)
FUTURE_EXIT = (77, 21)

# Each group raises one pad chain and sinks the other. Because a group is
# its own reciprocal, the pair can always be swapped back.
GROUPS = {
    # Raises a chain into the north ledge and sinks the one that lands on
    # the east bank. Gates the ledge's cache, never the route.
    "rapids_upper": {
        "switch": (38, 14),
        "opens": tuple((col, 12) for col in (43, 45, 47, 49, 51)),
        "closes": tuple((col, 26) for col in (43, 45, 47, 49, 51)),
        "chars": ("წ", "ჭ", "ხ"),
    },
    # Raises the only chain that reaches the way onward, and sinks the one
    # into the southern dead end. This flower is the crossing.
    "rapids_lower": {
        "switch": (57, 30),
        "opens": tuple((col, 20) for col in (63, 65, 67, 69)),
        "closes": tuple((col, 30) for col in (63, 65, 67, 69)),
        "chars": ("ჯ", "ჰ", "ჱ"),
    },
}

MOTHS = (((22, 15), "ჷ"), ((47, 20), "ჶ"), ((66, 24), "ჷ"))
ORCHID = (57, 7, "ჹ")
CACHES = ((58, 12), (74, 30))

HEADER = [
    "; PHASE 9 - FEYWILD 12, THE LUMINOUS RAPIDS (78x44 tiles).",
    "; Three crossings of one impassable river. The first is static stones",
    "; and one-tile jumps; the other two are twin lily-pad chains where a",
    "; flower raises one and sinks the other. Pollen thickens approaches",
    "; and never a landing tile. Every required landing is visible from",
    "; the tile before it - no blind jumps.",
]


def _room(grid, left, top, right, bottom, char="."):
    for row in range(top, bottom + 1):
        for col in range(left, right + 1):
            grid[row][col] = char


def _chain(grid, cells, char="ᚹ"):
    """Lay a crossing: safe cells with exactly one channel between each."""
    for index, (col, row) in enumerate(cells):
        grid[row][col] = char
        if index:
            previous = cells[index - 1]
            gap = ((col + previous[0]) // 2, (row + previous[1]) // 2)
            assert abs(col - previous[0]) + abs(row - previous[1]) == 2
            grid[gap[1]][gap[0]] = "≈"


def build() -> list[list[str]]:
    grid = [["#"] * W for _ in range(H)]

    # Banks and islands, then the three rivers carved between them.
    _room(grid, 1, 12, 14, 32)                 # the west bank
    _room(grid, 28, 8, 40, 36)                 # the middle isle
    _room(grid, 54, 16, 61, 34)                # the east bank
    _room(grid, 54, 8, 60, 14)                 # its walled north ledge
    # The far shore is deliberately in two pieces. Only the upper one
    # reaches the way onward, so the lower flower is the crossing.
    _room(grid, 71, 18, 71, 24)
    _room(grid, 71, 29, 71, 31)
    _room(grid, 72, 19, 76, 23)                # the way onward
    _room(grid, 72, 27, 76, 33)                # ...and the southern dead end
    for band in ((15, 6, 27, 38), (41, 4, 53, 38), (62, 6, 70, 34)):
        _room(grid, *band, "ᚼ")

    # Crossing one: static stones. The lesson the Fen already gave.
    _chain(grid, [(14, 21), (16, 21), (18, 21), (20, 21), (22, 21),
                  (24, 21), (26, 21), (28, 21)])

    # Crossings two and three: twin pad chains, one raised at a time. The
    # group's "opens" start furled -- solid, and visibly not yet safe.
    for group in GROUPS.values():
        for cells, char in ((group["opens"], "ᚧ"),
                            (group["closes"], "ᚨ")):
            ordered = sorted(cells)
            _chain(grid, ordered, char)
            first, last = ordered[0], ordered[-1]
            for end, step in ((first, -1), (last, 1)):
                col, row = end[0] + step, end[1]
                grid[row][col] = "≈"
                col += step
                if grid[row][col] == "ᚼ":
                    grid[row][col] = "ᚹ"

    # Pollen thickens the approaches. Never a landing tile: the beds are
    # laid before the crossings are cut back in, then any that strayed
    # onto stone, pad or channel is scrubbed out below.
    for left, top, right, bottom in ((3, 14, 12, 19), (30, 9, 38, 14),
                                     (30, 30, 39, 35), (55, 23, 60, 28)):
        for row in range(top, bottom + 1):
            for col in range(left, right + 1):
                if grid[row][col] != ".":
                    continue
                edge = min(col - left, right - col, row - top, bottom - row)
                if edge == 0 and (col * 7 + row * 13) % 3:
                    continue
                grid[row][col] = "☼"

    _dress_with_vegetation(grid)

    for (col, row), char in MOTHS:
        assert grid[row][col] == "ᚼ", (col, row, grid[row][col])
        grid[row][col] = char
    grid[ORCHID[1]][ORCHID[0]] = ORCHID[2]
    for col, row in CACHES:
        assert grid[row][col] in {".", "☼"}, (col, row)
        grid[row][col] = "<"

    for group in GROUPS.values():
        switch_char, open_char, close_char = group["chars"]
        col, row = group["switch"]
        grid[row][col] = switch_char
        for col, row in group["opens"]:
            grid[row][col] = open_char
        for col, row in group["closes"]:
            grid[row][col] = close_char

    for row in range(RETURN_EXIT[1] - 1, RETURN_EXIT[1] + 2):
        grid[row][RETURN_EXIT[0]] = "←"
    for row in range(FUTURE_EXIT[1] - 1, FUTURE_EXIT[1] + 2):
        grid[row][FUTURE_EXIT[0]] = "→"
    grid[ARRIVAL[1]][ARRIVAL[0]] = "ჲ"
    grid[ANCHOR[1]][ANCHOR[0]] = "ჳ"
    grid[FUTURE_RETURN[1]][FUTURE_RETURN[0]] = "ჵ"
    grid[FUTURE_EXIT[1]][FUTURE_EXIT[0]] = "ჴ"
    dress_grid("feywild_luminous_rapids", grid)
    plant_great_tree("feywild_luminous_rapids", grid)
    return grid


def _dress_with_vegetation(grid) -> None:
    for row in range(1, H - 1):
        for col in range(1, W - 1):
            if grid[row][col] != "#":
                continue
            if sum(grid[row + dr][col + dc] == "#"
                   for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1))) < 3:
                continue
            key = (col * 31 + row * 17) % 19
            if key == 0:
                grid[row][col] = "ŧ"
            elif key == 6:
                grid[row][col] = "Ŧ"
            elif key == 12:
                grid[row][col] = "Ɓ"


SOLID = {"#", "ᚼ", "ᚧ", "≈", "ŧ", "Ŧ", "Ɓ", "ŋ"}
LANDING = {"ᚹ", "ᚨ"}


def _base(grid, col, row) -> str:
    char = grid[row][col]
    for group in GROUPS.values():
        switch_char, open_char, close_char = group["chars"]
        if char == switch_char:
            return "."
        if char == open_char:
            return "ᚧ"
        if char == close_char:
            return "ᚨ"
    return {"ჲ": "'", "ჳ": ".", "ჴ": "→", "ჵ": "'", "<": ".",
            "ჶ": "ᚼ", "ჷ": "ᚼ", "ჸ": "#", "ჹ": "#"}.get(char, char)


def _open_tiles(grid, state):
    tiles = {(col, row)
             for row in range(H) for col in range(W)
             if _base(grid, col, row) not in SOLID}
    for group_id in state:
        group = GROUPS[group_id]
        tiles |= set(group["opens"])
        tiles -= set(group["closes"])
    return tiles


def _explore(grid):
    """BFS over (tile, group-state), with the walk-and-hop rule."""
    ids = tuple(GROUPS)
    open_by_state = {
        tuple(sorted(combo)): _open_tiles(grid, combo)
        for size in range(len(ids) + 1)
        for combo in product(ids, repeat=size)
    }
    origin = (ARRIVAL, ())
    nodes = {origin}
    backward = {}
    frontier = deque([origin])
    while frontier:
        tile, state = frontier.popleft()
        col, row = tile
        opens = open_by_state[state]
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            step = (col + dc, row + dr)
            land = (col + 2 * dc, row + 2 * dr)
            moves = []
            if step in opens:
                moves.append(step)
            # One committed hop clears exactly one channel cell.
            elif (0 <= land[0] < W and 0 <= land[1] < H
                    and _base(grid, *step) == "≈" and land in opens):
                moves.append(land)
            for destination in moves:
                node = (destination, state)
                backward.setdefault(node, []).append((tile, state))
                if node not in nodes:
                    nodes.add(node)
                    frontier.append(node)
        for group_id, group in GROUPS.items():
            switch = group["switch"]
            if abs(col - switch[0]) + abs(row - switch[1]) > 1:
                continue
            if tile in set(group["opens"]) | set(group["closes"]):
                continue
            active = set(state)
            active.symmetric_difference_update({group_id})
            node = (tile, tuple(sorted(active)))
            if tile not in open_by_state[node[1]]:
                continue
            backward.setdefault(node, []).append((tile, state))
            if node not in nodes:
                nodes.add(node)
                frontier.append(node)
    return nodes, backward


def validate(grid) -> None:
    assert len(grid) == H and all(len(row) == W for row in grid)

    for group_id, group in GROUPS.items():
        for col, row in group["opens"]:
            assert _base(grid, col, row) == "ᚧ", (group_id, col, row)
        for col, row in group["closes"]:
            assert _base(grid, col, row) == "ᚨ", (group_id, col, row)

    # Pollen slows an approach; it must never sit on something Chuck has
    # to land on, nor in a gap he has to clear.
    for row in range(H):
        for col in range(W):
            if grid[row][col] != "☼":
                continue
            for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                assert _base(grid, col + dc, row + dr) != "≈", (col, row)

    nodes, backward = _explore(grid)
    reached = {tile for tile, _state in nodes}
    assert FUTURE_EXIT in reached, "the rapids cannot be crossed"
    assert ANCHOR in reached and RETURN_EXIT in reached
    for cache in CACHES:
        assert cache in reached, cache

    # The river is a river: walking alone never gets across it.
    idle = _open_tiles(grid, ())
    walked = {ARRIVAL}
    frontier = deque([ARRIVAL])
    while frontier:
        col, row = frontier.popleft()
        for step in ((col - 1, row), (col + 1, row),
                     (col, row - 1), (col, row + 1)):
            if step in idle and step not in walked:
                walked.add(step)
                frontier.append(step)
    assert FUTURE_EXIT not in walked, "the rapids can be walked"

    # ...and jumping alone is not enough either: the lower flower must
    # be scratched before the way onward exists at all.
    hopped = {ARRIVAL}
    frontier = deque([ARRIVAL])
    while frontier:
        col, row = frontier.popleft()
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            step, land = (col + dc, row + dr), (col + 2 * dc, row + 2 * dr)
            if step in idle and step not in hopped:
                hopped.add(step)
                frontier.append(step)
            elif (0 <= land[0] < W and 0 <= land[1] < H
                    and _base(grid, *step) == "≈" and land in idle
                    and land not in hopped):
                hopped.add(land)
                frontier.append(land)
    assert FUTURE_EXIT not in hopped, "the rapids need no flower"
    assert CACHES[0] not in hopped

    # ...and no order of scratches can ever strand him mid-river.
    goals = {node for node in nodes if node[0] == FUTURE_EXIT}
    can_finish = set(goals)
    frontier = deque(goals)
    while frontier:
        node = frontier.popleft()
        for source in backward.get(node, ()):
            if source not in can_finish:
                can_finish.add(source)
                frontier.append(source)
    assert nodes == can_finish, sorted(nodes - can_finish)[:6]

    text = "".join("".join(row) for row in grid)
    assert text.count("ჳ") == 1
    assert text.count("<") == len(CACHES)
    assert sum(text.count(char) for char in {c for _pos, c in MOTHS}) == len(MOTHS)
    # Orchids are a late/optional flourish here, not a gate.
    assert text.count("ჸ") + text.count("ჹ") == 1
    assert all(grid[row][0] == "←"
               for row in range(RETURN_EXIT[1] - 1, RETURN_EXIT[1] + 2))
    assert all(grid[row][W - 1] in {"→", "ჴ"}
               for row in range(FUTURE_EXIT[1] - 1, FUTURE_EXIT[1] + 2))


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
