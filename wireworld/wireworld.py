import argparse
import contextlib
import enum
import itertools as it
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

moore_offsets = [(x, y) for x, y in it.product(*it.repeat(range(-1,2), 2)) if x or y]

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
            for (dx, dy) in moore_offsets:
                neighbor_position = (x + dx, y + dy)
                if neighbor_position in world:
                    data['neighbors'].append(neighbor_position)
        return world

def next_state(world, cell):
    if cell['state'] == CellState.H:
        return CellState.T
    elif cell['state'] == CellState.T:
        return CellState.C
    else:
        # is conductor
        head_neighbors = sum(
            1 for neighbor_position in cell['neighbors']
            if world[neighbor_position]['state'] == CellState.H
        )
        if head_neighbors in (1, 2):
            return CellState.H
        else:
            return CellState.C

def step(world):
    newworld = {
        pos: {
            'state': next_state(world, data),
            'neighbors': data['neighbors'],
        }
        for pos, data in world.items()
    }
    return newworld

def run(world):
    original = world
    screen = pygame.display.set_mode((512,)*2)
    window = screen.get_rect()
    clock = pygame.time.Clock()
    step_time = 100
    step_elapsed = 0
    running = True
    while running:
        elapsed = clock.tick()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
        step_elapsed += elapsed
        if step_elapsed >= step_time:
            step_elapsed = 0
            world = step(world)
        # draw
        screen.fill('black')
        scale = 20
        for (i, j), cell in world.items():
            screen_pos = (i * scale, j * scale)
            color = cell['state'].color
            rect = pygame.Rect(screen_pos, (scale, scale))
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, 'gray', rect, 1)

        pygame.display.flip()

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
