import argparse
import contextlib
import itertools as it
import math
import os
import unittest

from collections import defaultdict

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

deltas = set(tuple(x - 1 for x in divmod(i, 3)) for i in range(9))
deltas.remove((0,0))

blinker_string = '\n'.join([
    '###',
])

angel_string = '\n'.join([
    '  #  ',
    '## ##',
    ' # # ',
    '  #  ',
])

# https://www.reddit.com/r/GameOfLifePatterns/comments/rn5949/found_this_cool_pattern_looks_like_a_running/
washing_machine_string = '\n'.join([
    '       #        ',
    '      # #       ',
    '       ##       ',
    '      #  #      ',
    '     # ## #     ',
    '    # #### #    ',
    '   # #    # # # ',
    ' ## ## ## ## # #',
    '# # ## ## ## ## ',
    ' # # #    # #   ',
    '    # #### #    ',
    '     # ## #     ',
    '      #  #      ',
    '       ##       ',
    '       # #      ',
    '        #       ',
])

class TestBlinker(unittest.TestCase):

    def test_blinker(self):
        state = blinker()
        self.assertEqual(state, {(1,0), (1,1), (1,2)})
        state = evolve(state)
        self.assertEqual(state, {(0,1), (1,1), (2,1)})
        state = evolve(state)
        self.assertEqual(state, {(1,0), (1,1), (1,2)})


def string_iter(s):
    for row, line in enumerate(s.splitlines()):
        for col, char in enumerate(line):
            pos = (row, col)
            yield (pos, char)

def pattern_from_string(s):
    for pos, char in string_iter(s):
        if char != ' ':
            yield pos

def blinker():
    return set(pattern_from_string(blinker_string))

def angel():
    return set(pattern_from_string(angel_string))

def washing_machine():
    return set(pattern_from_string(washing_machine_string))

def is_alive(state, other, count):
    return (
        (count in {2, 3} and other in state)
        or
        (count == 3 and other not in state)
    )

def neighbor_counts(state):
    counts = defaultdict(int)
    for row, col in state:
        for drow, dcol in deltas:
            other = (row + drow, col + dcol)
            counts[other] += 1
    return counts

def evolve(state):
    neighbors = neighbor_counts(state)
    container = type(state)
    return container(
        other for other, count in neighbors.items()
        if is_alive(state, other, count)
    )

def evolve_generator(state):
    """
    Generate evolving states with their indexes. After a duplicate is detected
    states are taken from a list with repeating indexes.
    """
    yield (state, 0)

    states = [state]
    for index in it.count(1):
        state = evolve(state)
        if state in states:
            start_index = states.index(state)
            break
        else:
            states.append(state)
            yield (state, index)

    repeating_indexes = it.cycle(range(start_index, len(states)))
    for index in repeating_indexes:
        yield (states[index], index)

def run(pattern, cell_size=None, step_speed=None):
    pygame.font.init()
    screen = pygame.display.set_mode((500,)*2)
    frame = screen.get_rect()
    clock = pygame.time.Clock()
    framerate = 60
    font = pygame.font.SysFont('monospace', 30)

    states = evolve_generator(pattern)
    if step_speed is None:
        step_speed = math.inf

    if cell_size is None:
        cell_size = (40,)*2
    cell = pygame.Rect((0, 0), cell_size)
    game_rect = pygame.Rect((0,)*4)
    frame_number = 0
    time = math.inf
    running = True
    while running:
        elapsed = clock.tick(framerate)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                elif event.key == pygame.K_r:
                    states = evolve_generator(pattern)
                    time = math.inf
                elif event.key == pygame.K_s and step_speed is math.inf:
                    state, index = next(states)

        time += elapsed
        if time >= step_speed:
            time = 0
            state, index = next(states)

        # draw
        screen.fill('grey30')

        def make_rect(row, col):
            x = col * cell.width
            y = row * cell.height
            return pygame.Rect((x, y), cell.size)

        rects = [make_rect(row, col) for row, col in state]
        wrapped = pygame.Rect((0,)*4).unionall(rects)
        if wrapped.size > game_rect.size:
            game_rect.size = wrapped.size
            game_rect.center = frame.center

            grid_lines = set()
            xs = range(game_rect.x % cell.width, frame.right, cell.width)
            ys = range(game_rect.y % cell.height, frame.bottom, cell.height)
            for x, y in it.product(xs, ys):
                start = (frame.left, y)
                end = (frame.right, y)
                grid_lines.add((start, end))

                start = (x, frame.top)
                end = (x, frame.bottom)
                grid_lines.add((start, end))

        offset = pygame.Vector2(game_rect.topleft)
        for rect in rects:
            rect.topleft += offset

        for rect in rects:
            pygame.draw.rect(screen, 'azure', rect)

        for start, end in grid_lines:
            pygame.draw.line(screen, 'black', start, end)

        lines = [
            f'{index=}',
            f'{frame_number=}',
            f'FPS: {clock.get_fps():.2f}',
        ]
        images = [font.render(line, True, 'white') for line in lines]
        rects = [image.get_rect() for image in images]

        for r1, r2 in it.pairwise(rects):
            r2.topright = r1.bottomright

        wrapped = pygame.Rect((0,)*4).unionall(rects)
        positioned = wrapped.copy()
        positioned.bottomright = frame.bottomright

        delta = pygame.Vector2(positioned.topleft) - wrapped.topleft

        for rect in rects:
            rect.topleft += delta

        for image, rect in zip(images, rects):
            screen.blit(image, rect)

        pygame.display.update()

        frame_number += 1

def main(argv=None):
    """
    Animated game of life.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('pattern', choices=['blinker', 'angel', 'washing_machine'])
    parser.add_argument('--step', type=int)
    args = parser.parse_args(argv)
    pattern_func = eval(args.pattern)
    pattern = pattern_func()
    run(pattern, args.step)

if __name__ == '__main__':
    main()

# 2023-11-23
# - https://realpython.com/conway-game-of-life-python/
