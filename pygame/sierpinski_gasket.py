# https://oeis.org/wiki/Python_Program_to_generate_the_Sierpinski%27s_gasket
# 2025-06-28:
# - Code seasoned to (my) taste.

import contextlib
import logging
import os
import random

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

def random_choice_from_set(set_):
    index = random.randrange(len(set_))
    for i, element in enumerate(set_):
        if i == index:
            return element

logging.basicConfig(level=logging.INFO)

screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption('Sierpinski Triangle')

denominator = 2
min_denom = 2
seed = None
clicked = set()
drawn = set()
failed = 0
running = True
restart = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_DOWN):
                if event.key == pygame.K_UP:
                    denominator += 1
                    logging.info('denominator: %s', denominator)
                    restart = True
                elif event.key == pygame.K_DOWN:
                    if denominator > min_denom:
                        denominator -= 1
                        logging.info('denominator: %s', denominator)
                        restart = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                if event.pos not in clicked:
                    clicked.add(event.pos)
                    screen.fill('black')
                    for point in clicked:
                        screen.set_at(point, 'white')
                    seed = None
            elif event.button == pygame.BUTTON_RIGHT:
                clicked.clear()
                screen.fill('black')
            pygame.display.update()
            drawn.clear()
            failed = 0

    if restart:
        restart = False
        failed = 0
        screen.fill('black')
        pygame.display.update()
        drawn.clear()

    if failed < 60 and len(clicked) > 1:
        if seed is None:
            seed = random_choice_from_set(clicked)
        point = random_choice_from_set(clicked)

        if (point, seed) in drawn:
            failed += 1
            if failed == 60:
                logging.info('giving up')
        else:
            drawn.add((point, seed))
            seed = (
                (seed[0] + point[0]) // denominator,
                (seed[1] + point[1]) // denominator,
            )
            if 0 <= seed[0] <= 800 and 0 <= seed[1] <= 800:
                screen.set_at(seed, 'red')
                pygame.display.update()
                logging.info('%s', seed)
            else:
                failed += 1
                if failed == 60:
                    logging.info('giving up')
