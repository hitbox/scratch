import argparse
import contextlib
import enum
import itertools as it
import operator as op
import os

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

class CellState(enum.Enum):
    H = enum.auto()
    T = enum.auto()
    C = enum.auto()


CellState.H.color = 'blue'
CellState.T.color = 'red'
CellState.C.color = 'yellow'

deltas = [tuple(v - 1 for v in divmod(i, 3)) for i in range(9)]
deltas.remove((0,0))

def world_from_file(obj):
    """
    Load world from text file.
    """

    def is_comment(line):
        return line.strip().startswith('#')

    def is_not_comment(line):
        return not is_comment(line)

    namemap = {member.name: member for member in CellState}
    with open(obj) as file:
        lines = filter(is_not_comment, file)
        world = {
            (x, y): {
                'state': namemap[char],
                'neighbors': list(),
            }
            for y, line in enumerate(lines)
            for x, char in enumerate(line)
            if char in namemap
        }
        for (x, y), data in world.items():
            for (dx, dy) in deltas:
                neighbor_position = (x + dx, y + dy)
                if neighbor_position in world:
                    data['neighbors'].append(neighbor_position)
        return world

def next_state(world, cell):
    if cell['state'] == CellState.H:
        # H -> T
        return CellState.T
    elif cell['state'] == CellState.T:
        # T -> C
        return CellState.C
    else:
        # C -> H if num H neighbors equals one or two, otherwise C
        head_neighbors = sum(
            1 for neighbor_position in cell['neighbors']
            if world[neighbor_position]['state'] == CellState.H
        )
        if head_neighbors in (1, 2):
            return CellState.H
        else:
            return CellState.C

def step(world):
    new_world = {
        pos: {
            'state': next_state(world, data),
            'neighbors': data['neighbors'],
        }
        for pos, data in world.items()
    }
    return new_world

def wrap_rects(rects):
    sides = op.attrgetter('top', 'right', 'bottom', 'left')
    tops, rights, bottoms, lefts = zip(*map(sides, rects))
    top = min(tops)
    right = max(rights)
    bottom = max(bottoms)
    left = min(lefts)
    width = right - left
    height = bottom - top
    return (left, top, width, height)

def get_rect(rect=None, **kwargs):
    if rect is None:
        rect = pygame.Rect((0,)*4)
    else:
        rect = rect.copy()
    for key, val in kwargs.items():
        setattr(rect, key, val)
    return rect

def update_as_one(rects, **kwargs):
    origin = pygame.Rect(wrap_rects(rects))
    dest = get_rect(origin, **kwargs)
    delta = pygame.Vector2(dest.topleft) - origin.topleft
    for rect in rects:
        rect.topleft += delta

def run(world):
    screen = pygame.display.set_mode((512,)*2)
    window = screen.get_rect()
    clock = pygame.time.Clock()
    framerate = 60

    scale = 22
    cell_rects = [pygame.Rect((i*scale, j*scale), (scale,)*2) for (i, j) in world]
    update_as_one(cell_rects, center=window.center)

    def draw():
        screen.fill('black')
        for cell, rect in zip(world.values(), cell_rects):
            color = cell['state'].color
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, 'gray', rect, 1)
        pygame.display.flip()
    draw()

    frame = 0
    running = True
    while running:
        clock.tick(framerate)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
        frame = (frame + 1) % (framerate // 8)
        if frame == 0:
            world = step(world)
            draw()

def main(argv=None):
    """
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('world')
    args = parser.parse_args()

    world = world_from_file(args.world)
    run(world)

if __name__ == '__main__':
    main()

# 2023-10-11
# - via feedly
#   https://spritely.institute/news/scheme-wireworld-in-browser.html
#   https://spritely.institute/news/hoot-wireworld-live-in-browser.html
#   https://en.wikipedia.org/wiki/Wireworld
# - Another "I wanna do this with Python," project.
