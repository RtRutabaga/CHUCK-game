"""Author Feywild 9: the Shifting Hedge, the phase's navigation puzzle.

A single ring corridor runs around a great hedge, gated at its four
corners. Two gates start open and two start shut, so the ring is never a
simple lap: each flower trades one doorway for another, and the player
learns the hedge by reasoning about which trade is worth making.

Nothing here is random. The validator walks the whole state space --
every tile in every combination of the four groups -- and proves three
things: the exit can be reached, the optional pocket can be reached, and
from every state Chuck can possibly reach, the exit is still reachable.
That last check is the one that matters: it is a proof that no sequence
of scratches can ever strand him.
"""

from collections import deque
from itertools import product
from pathlib import Path

W, H = 68, 44
OUT = (
    Path(__file__).resolve().parents[1]
    / "assets" / "maps" / "feywild_shifting_hedge.txt"
)

RETURN_EXIT = (0, 22)
ARRIVAL = (1, 22)
ANCHOR = (8, 22)
FUTURE_RETURN = (66, 22)
FUTURE_EXIT = (67, 22)

# Each group: the flower, the hedge it opens, the hedge it closes. Every
# group is its own reciprocal, so a second scratch always undoes the
# first -- that is what keeps the puzzle safe rather than sequential.
GROUPS = {
    "hedge_north": {
        "switch": (30, 9),
        "opens": ((43, 8), (43, 9), (43, 10)),     # the north-east gate
        "closes": ((25, 8), (25, 9), (25, 10)),    # the north-west gate
        "chars": ("ა", "ბ", "გ"),
    },
    "hedge_south": {
        "switch": (30, 35),
        "opens": ((25, 34), (25, 35), (25, 36)),   # the south-west gate
        "closes": ((43, 34), (43, 35), (43, 36)),  # the south-east gate
        "chars": ("დ", "ე", "ვ"),
    },
    "hedge_east": {
        "switch": (55, 28),
        "opens": ((57, 21), (57, 22), (57, 23)),   # the way out
        "closes": ((54, 16), (55, 16), (56, 16)),  # the eastern run, severed
        "chars": ("ზ", "თ", "ი"),
    },
    "hedge_west": {
        "switch": (20, 35),
        "opens": ((20, 33),),                      # into the quiet pocket
        "closes": ((17, 34), (17, 35), (17, 36)),  # the run back west
        "chars": ("კ", "ლ", "მ"),
    },
}

POCKET_GRASS = ((19, 30), (21, 31))
MITES = ((18, 9), (38, 9), (55, 20), (35, 35))

HEADER = [
    "; PHASE 9 - FEYWILD 9, THE SHIFTING HEDGE (68x44 tiles).",
    "; One ring corridor, gated at four corners; two gates start open.",
    "; Each flower opens one hedge doorway and closes another, and a second",
    "; scratch always undoes it, so no sequence of changes can trap Chuck.",
    "; The hedge is fixed and inspectable - never randomised.",
]


def _room(grid, left, top, right, bottom, char="'"):
    for row in range(top, bottom + 1):
        for col in range(left, right + 1):
            grid[row][col] = char


def build() -> list[list[str]]:
    grid = [["#"] * W for _ in range(H)]

    # The ring: one corridor all the way around the central hedge mass.
    _room(grid, 12, 8, 56, 10)
    _room(grid, 12, 34, 56, 36)
    _room(grid, 12, 8, 14, 36)
    _room(grid, 54, 8, 56, 36)

    # The clearings at either end, and the quiet pocket off the south run.
    _room(grid, 1, 20, 11, 24, ".")
    _room(grid, 11, 21, 12, 23)
    _room(grid, 58, 21, 66, 23)
    _room(grid, 18, 29, 22, 32, ".")

    _dress_with_vegetation(grid)

    # Two of the four corner gates start open; the other two are hedge.
    for col, row in ((25, 8), (25, 9), (25, 10),
                     (43, 34), (43, 35), (43, 36)):
        grid[row][col] = "'"
    for col, row in ((43, 8), (43, 9), (43, 10),
                     (25, 34), (25, 35), (25, 36)):
        grid[row][col] = "#"

    for group in GROUPS.values():
        switch_char, open_char, close_char = group["chars"]
        col, row = group["switch"]
        grid[row][col] = switch_char
        for col, row in group["opens"]:
            assert grid[row][col] == "#", (col, row)
            grid[row][col] = open_char
        for col, row in group["closes"]:
            assert grid[row][col] in {"'", "."}, (col, row)
            grid[row][col] = close_char

    for col, row in POCKET_GRASS:
        grid[row][col] = "<"
    for col, row in MITES:
        grid[row][col] = "რ"

    for row in range(RETURN_EXIT[1] - 1, RETURN_EXIT[1] + 2):
        grid[row][RETURN_EXIT[0]] = "←"
    for row in range(FUTURE_EXIT[1] - 1, FUTURE_EXIT[1] + 2):
        grid[row][FUTURE_EXIT[0]] = "→"
    grid[ARRIVAL[1]][ARRIVAL[0]] = "ნ"
    grid[ANCHOR[1]][ANCHOR[0]] = "ო"
    grid[FUTURE_RETURN[1]][FUTURE_RETURN[0]] = "ჟ"
    grid[FUTURE_EXIT[1]][FUTURE_EXIT[0]] = "პ"
    return grid


def _dress_with_vegetation(grid) -> None:
    """The region's trees and shrubs, only well inside the hedge mass."""
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


SOLID = {"#", "ŧ", "Ŧ", "Ɓ"}


def _base_char(grid, col, row) -> str:
    char = grid[row][col]
    for group in GROUPS.values():
        switch_char, open_char, close_char = group["chars"]
        if char == switch_char:
            return "."
        if char == open_char:
            return "#"
        if char == close_char:
            return "'"
    return {"ნ": "'", "ო": ".", "პ": "→", "ჟ": "'", "რ": ".",
            "<": "."}.get(char, char)


def _open_tiles(grid, state):
    """Which tiles are walkable in one combination of group states."""
    open_set = {
        (col, row)
        for row in range(H) for col in range(W)
        if _base_char(grid, col, row) not in SOLID
    }
    for group_id, active in state.items():
        if not active:
            continue
        group = GROUPS[group_id]
        open_set |= set(group["opens"])
        open_set -= set(group["closes"])
    return open_set


def _explore(grid):
    """BFS the whole (tile, group-state) space; return nodes and edges."""
    ids = tuple(GROUPS)
    states = [dict(zip(ids, combo))
              for combo in product((False, True), repeat=len(ids))]
    open_by_state = {
        tuple(sorted(k for k, v in state.items() if v)): _open_tiles(grid, state)
        for state in states
    }

    def key(state):
        return tuple(sorted(k for k, v in state.items() if v))

    start_state = {group_id: False for group_id in ids}
    start = (ARRIVAL, key(start_state))
    nodes = {start}
    edges = []
    frontier = deque([start])
    while frontier:
        (tile, state_key) = frontier.popleft()
        col, row = tile
        opens = open_by_state[state_key]
        for step in ((col - 1, row), (col + 1, row),
                     (col, row - 1), (col, row + 1)):
            if step not in opens:
                continue
            node = (step, state_key)
            edges.append(((tile, state_key), node))
            if node not in nodes:
                nodes.add(node)
                frontier.append(node)
        for group_id, group in GROUPS.items():
            switch = group["switch"]
            if tile != switch and abs(col - switch[0]) + abs(row - switch[1]) > 1:
                continue
            # The controller refuses to change a tile Chuck is standing on.
            if tile in set(group["opens"]) | set(group["closes"]):
                continue
            active = set(state_key)
            active.symmetric_difference_update({group_id})
            node = (tile, tuple(sorted(active)))
            if tile not in open_by_state[node[1]]:
                continue
            edges.append(((tile, state_key), node))
            if node not in nodes:
                nodes.add(node)
                frontier.append(node)
    return nodes, edges


def validate(grid) -> None:
    assert len(grid) == H and all(len(row) == W for row in grid)

    # Every group must genuinely trade: open something shut, shut
    # something open. The controller enforces this too, loudly.
    for group_id, group in GROUPS.items():
        for col, row in group["opens"]:
            assert _base_char(grid, col, row) in SOLID, (group_id, col, row)
        for col, row in group["closes"]:
            assert _base_char(grid, col, row) not in SOLID, (group_id, col, row)

    # The hedge must actually be a puzzle: standing still solves nothing.
    idle = _open_tiles(grid, {group_id: False for group_id in GROUPS})
    walked = {ARRIVAL}
    frontier = deque([ARRIVAL])
    while frontier:
        col, row = frontier.popleft()
        for step in ((col - 1, row), (col + 1, row),
                     (col, row - 1), (col, row + 1)):
            if step in idle and step not in walked:
                walked.add(step)
                frontier.append(step)
    assert FUTURE_EXIT not in walked, "the hedge can be walked straight through"
    assert not any(grass in walked for grass in POCKET_GRASS)

    nodes, edges = _explore(grid)
    tiles_reached = {tile for tile, _state in nodes}
    assert FUTURE_EXIT in tiles_reached, "the hedge cannot be solved"
    assert ANCHOR in tiles_reached
    assert RETURN_EXIT in tiles_reached
    for grass in POCKET_GRASS:
        assert grass in tiles_reached, grass
    for mite in MITES:
        assert mite in tiles_reached, mite

    # The safety proof: from every state Chuck can reach, he can still
    # reach the exit. No scratch, in any order, can ever strand him.
    backward = {}
    for source, target in edges:
        backward.setdefault(target, []).append(source)
    goals = {node for node in nodes if node[0] == FUTURE_EXIT}
    can_finish = set(goals)
    frontier = deque(goals)
    while frontier:
        node = frontier.popleft()
        for source in backward.get(node, ()):
            if source not in can_finish:
                can_finish.add(source)
                frontier.append(source)
    stranded = nodes - can_finish
    assert not stranded, sorted(stranded)[:6]

    text = "".join("".join(row) for row in grid)
    assert text.count("ო") == 1
    assert text.count("<") == len(POCKET_GRASS)
    assert text.count("რ") == len(MITES)
    assert all(grid[row][0] == "←"
               for row in range(RETURN_EXIT[1] - 1, RETURN_EXIT[1] + 2))
    assert all(grid[row][W - 1] in {"→", "პ"}
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
