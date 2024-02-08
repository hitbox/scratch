import argparse
import enum
import operator as op

import pygamelib

from pygamelib import pygame

class CellState(enum.Enum):

    HEAD = enum.auto()
    TAIL = enum.auto()
    COPPER = enum.auto()


CellState.HEAD.color = 'blue'
CellState.TAIL.color = 'red'
CellState.COPPER.color = 'yellow'

def world_from_file(obj):
    """
    Load world from text file.
    """

    def is_comment(line):
        return line.strip().startswith('#')

    def is_not_comment(line):
        return not is_comment(line)

    namemap = {member.name[0]: member for member in CellState}
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
            for (dx, dy) in pygamelib.DELTAS:
                neighbor_position = (x + dx, y + dy)
                if neighbor_position in world:
                    data['neighbors'].append(neighbor_position)
        return world

def next_state(world, cell):
    if cell['state'] == CellState.HEAD:
        # HEAD -> TAIL
        return CellState.TAIL
    elif cell['state'] == CellState.TAIL:
        # TAIL -> COPPER
        return CellState.COPPER
    else:
        # COPPER -> HEAD if num HEAD neighbors equals one or two, otherwise COPPER
        head_neighbors = sum(
            1 for neighbor_position in cell['neighbors']
            if world[neighbor_position]['state'] == CellState.HEAD
        )
        if head_neighbors in (1, 2):
            return CellState.HEAD
        else:
            return CellState.COPPER

def step(world):
    new_world = {
        pos: {
            'state': next_state(world, data),
            'neighbors': data['neighbors'],
        }
        for pos, data in world.items()
    }
    return new_world

def run(display_size, world):
    screen = pygame.display.set_mode(display_size)
    window = screen.get_rect()
    clock = pygame.time.Clock()
    framerate = 60

    scale = 22
    cell_rects = [pygame.Rect((i*scale, j*scale), (scale,)*2) for (i, j) in world]
    pygamelib.move_as_one(cell_rects, center=window.center)

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
    parser = pygamelib.command_line_parser()
    parser.add_argument('world', help='Wireworld file.')
    args = parser.parse_args()
    world = world_from_file(args.world)
    run(args.display_size, world)

if __name__ == '__main__':
    main()

# 2023-10-11
# - via feedly
#   https://spritely.institute/news/scheme-wireworld-in-browser.html
#   https://spritely.institute/news/hoot-wireworld-live-in-browser.html
#   https://en.wikipedia.org/wiki/Wireworld
# - Another "I wanna do this with Python," project.
# 2024-02-08 Thu.
# - a wireworld editor
# - there's surely a clever little game in here somewhere
