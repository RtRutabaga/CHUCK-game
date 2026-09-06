"""Where the pieces of a fallen building end up.

Shared by the hub and the undead ruins, for the reason the eastern
maps share their seam frayer: two maps that dress their ruins by
different rules read as two different kinds of ruin, and the whole
point of the hub's scattered rectangles is that they are fragments of
the building south of it.

The rule is about *where*, not about *what*. A ruin that has had
columns dropped into the middle of it looks like a warehouse; what
makes a ruin look ruined is that its pieces went outward. So the
columns stand at the corners, where the load was, and the rubble is
outside the wall it came off, lying on the sand -- and one column has
come down full length across the floor, which is the single loudest
thing in the vocabulary and is therefore used once per building.

Nothing here is ever placed on a tile that already has something on
it. A ruin is the least important thing on any of these maps and it
must never be the reason a doorway closed.
"""

COLUMN = "⍏"           # standing on buried flagstones
COLUMN_SAND = "⍐"      # ...and standing out on the sand
FALLEN = "⍖"
FALLEN_SAND = "⍗"
RUBBLE = "⍓"
RUBBLE_SAND = "⍔"

FLOOR = "⌖"
GROUND = (".", ",", "⟁")


def _place(grid, x: int, y: int, on_floor: str, on_sand: str) -> bool:
    """One piece, if the tile is free ground. Returns whether it went."""
    height = len(grid)
    width = len(grid[0])
    if not (0 <= y < height and 0 <= x < width):
        return False
    if grid[y][x] == FLOOR:
        grid[y][x] = on_floor
        return True
    if grid[y][x] in GROUND:
        grid[y][x] = on_sand
        return True
    return False


def dress_ruin(grid, left: int, top: int, width: int, height: int,
               *, seed: int = 0) -> int:
    """Stand columns at one building's corners and spill its blocks.

    `left, top, width, height` is the walled rectangle itself; the
    buried floor is assumed to run one tile outside it, which is how
    both generators lay a ruin down.

    The seed decides which corners kept their columns. All four is a
    colonnade -- a building that is still standing -- and the same two
    on every ruin is a stencil, so it varies, and it varies with the
    ruin's own position so a map redraws the same way twice.
    """
    placed = 0
    ring_left, ring_top = left - 1, top - 1
    ring_right, ring_bottom = left + width, top + height
    corners = ((ring_left, ring_top), (ring_right, ring_top),
               (ring_left, ring_bottom), (ring_right, ring_bottom))
    # Two or three of the four, never all of them.
    keep = ((0, 2), (1, 3), (0, 1, 3), (0, 2, 3), (1, 2))[seed % 5]
    for index in keep:
        placed += _place(grid, *corners[index], COLUMN, COLUMN_SAND)

    # ...and one more standing part way along a side, so the columns
    # are not only ever at the four corners. Which side depends on the
    # ruin, because a column at the same place on every building is a
    # stencil and reads as one.
    sides = ((left + width // 3, ring_top),
             (left + 2 * width // 3, ring_bottom),
             (ring_left, top + height // 2),
             (ring_right, top + height // 3))
    placed += _place(grid, *sides[seed % 4], COLUMN, COLUMN_SAND)

    # One column down full length, inside, across the middle. It is the
    # loudest thing here, so there is one per building: two of them in
    # the same room and the room reads as a quarry.
    placed += _place(grid, left + width // 2 + seed % 2,
                     top + height // 2, FALLEN, FALLEN_SAND)
    # ...and one that came down outside the wall, which is the version
    # of the same event you can walk all the way round.
    placed += _place(grid, left + (seed * 2) % max(1, width),
                     top + height + 2, FALLEN, FALLEN_SAND)

    # Blocks off the wall, on the sand outside it. Outward, always:
    # rubble tidied inside the footprint is a builder's yard.
    spills = (
        (left + width + 1, top + (height + seed) % max(1, height)),
        (left - 2, top + (height + seed * 2) % max(1, height)),
        (left + (width + seed) % max(1, width), top + height + 1),
        (left + (width + seed * 3) % max(1, width), top - 2),
        (left + width + 2, top + (seed * 5) % max(1, height)),
        (left - 3, top + (seed * 7) % max(1, height)),
        (left + (width + seed * 4) % max(1, width), top + height + 3),
        (left + (width + seed * 6) % max(1, width), top - 1),
    )
    for index, (x, y) in enumerate(spills):
        if (index + seed) % 4 == 3:
            continue        # not every side of every ruin lost a piece
        placed += _place(grid, x, y, RUBBLE, RUBBLE_SAND)
    return placed
