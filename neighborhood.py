# Saw this lua function
# https://github.com/heav-4/relocation/blob/main/src/main.lua#L33
# see also: /home/hitbox/repos/reference/heav-4/relocation

relatives = list(tuple(reversed(divmod(i, 3))) for i in range(9))

def neighborhood_from_topleft(x, y):
    for i in range(9):
        dy, dx = divmod(i, 3)
        yield (x+dx, y+dy)

def neighborhood_from_center(x, y):
    for i in range(9):
        dy, dx = divmod(i, 3)
        yield (x+dx-1, y+dy-1)

a = set(neighborhood_from_center(0,0))
b = set([
    (-1, -1), (0, -1), (1, -1),
    (-1,  0), (0,  0), (1,  0),
    (-1,  1), (0,  1), (1,  1),
])
assert a == b, a
