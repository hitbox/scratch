import argparse
import contextlib
import math
import os
import unittest

from collections import defaultdict

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

deltas = set(tuple(x - 1 for x in divmod(i, 3)) for i in range(9))
deltas.remove((0,0))

class TestBlinker(unittest.TestCase):

    def test_blinker(self):
        state = blinker()
        self.assertEqual(state, {(1,0), (1,1), (1,2)})
        state = evolve(state)
        self.assertEqual(state, {(0,1), (1,1), (2,1)})
        state = evolve(state)
        self.assertEqual(state, {(1,0), (1,1), (1,2)})


def one_indexed(cells):
    return {(row-1, col-1) for row, col in cells}

def blinker():
    return one_indexed({(2,1), (2,2), (2,3)})

def angel():
    return one_indexed({
                      (1,3),
        (2,1), (2,2),        (2,4), (2,5),
               (3,2),        (3,4),
                      (4,3),
    })

def griditer(state):
    rows, cols = zip(*state)
    for row in range(min(rows), max(rows)+1):
        for col in range(min(cols), max(cols)+1):
            yield (row, col)

def alive_neighbors(state, row, col):
    neighbor_positions = ((row + dy, col + dx) for dy, dx in deltas)
    return {other for other in neighbor_positions if other in state}

def evolve(state):
    neighbor_counts = defaultdict(int)
    for row, col in state:
        for drow, dcol in deltas:
            other = (row + drow, col + dcol)
            neighbor_counts[other] += 1

    def is_alive(other, count):
        return (
            (count in {2, 3} and other in state)
            or
            (count == 3 and other not in state)
        )

    return {other for other, count in neighbor_counts.items() if is_alive(other, count)}

def draw(font, time, state, screen):
    screen.fill('black')
    frame = screen.get_rect()

    width = 10
    height = 10
    def make_rect(row, col):
        x = 100 + col * width
        y = 100 + row * height
        return pygame.Rect(x, y, width, height)

    rects = [make_rect(row, col) for row, col in state]
    for rect in rects:
        pygame.draw.rect(screen, 'white', rect)
        pygame.draw.rect(screen, 'black', rect, 1)

    image = font.render(f'{time=}', True, 'white')
    screen.blit(image, image.get_rect(bottomright=frame.bottomright))

    pygame.display.update()

def run():
    pygame.font.init()
    screen = pygame.display.set_mode((500,)*2)
    clock = pygame.time.Clock()
    framerate = 60
    font = pygame.font.SysFont('monospace', 30)

    state = angel()
    state_time = 1

    time = math.inf
    running = True
    while running:
        elapsed = clock.tick(framerate)
        time += elapsed
        if time >= 500:
            state_time += 1
            state = evolve(state)
            time = 0
            draw(font, state_time, state, screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)
    run()

if __name__ == '__main__':
    main()

# 2023-11-23
# - https://realpython.com/conway-game-of-life-python/
