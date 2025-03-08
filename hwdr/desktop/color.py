BLACK = 0
DARK_BLUE = 1
DARK_PURPLE = 2
DARK_GREEN = 3
BROWN = 4
DARK_GRAY = 5
GRAY = 6
WHITE = 7
RED = 8
ORANGE = 9
YELLOW = 10
GREEN = 11
BLUE = 12
INDIGO = 13
PINK = 14
PEACH = 15

PALETTE = (
 (0, 0, 0),
 (29, 43, 83),
 (126, 37, 83),
 (0, 135, 81),
 (171, 82, 54),
 (95, 87, 79),
 (194, 195, 199),
 (255, 241, 232),
 (255, 0, 77),
 (255, 163, 0),
 (255, 236, 39),
 (0, 228, 54),
 (41, 173, 255),
 (131, 118, 156),
 (255, 119, 168),
 (255, 204, 170)
)

mask = Box(
 bit = 0b0000000000000001,
)

def transparent(color=-1, hide=False):
 global mask
 if color == -1:
  mask.bit = 1
 elif hide:
  mask.bit |= (1 << color)
 else:
  mask.bit &= ~(1 << color)
