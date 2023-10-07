# NOTE: IDK, starting with topleft does not seem like the starting point of clockwise
CORNERS = ['topright', 'bottomright', 'bottomleft', 'topleft']

# ensure left-to-right, top-to-bottom for unpacking
LINES = [
    ('topleft', 'topright'),
    ('topright', 'bottomright'),
    ('bottomleft', 'bottomright'),
    ('topleft', 'bottomleft'),
]

MIDPOINTS = ['midtop', 'midright', 'midbottom', 'midleft']

POINTS = [
    'midtop', 'topright', 'midright', 'bottomright', 'midbottom', 'bottomleft',
    'midleft', 'topleft'
]

# clockwise sorted list of directions
# arranged such that +2 "around" it is the opposite side.
SIDES = ['top', 'right', 'bottom', 'left']


