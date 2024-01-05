import argparse
import contextlib
import itertools as it
import math
import os
import random

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

rect_ops = ['clip', 'union']
rect_fills = [0, 1]

def run(op):
    screen = pygame.display.set_mode((800,)*2)
    window = screen.get_rect()
    clock = pygame.time.Clock()
    framerate = 60
    space = window.inflate((-100,)*2)
    fill = rect_fills[rect_ops.index(op)]

    rects = [
        space.inflate((-500,)*2),
        space.inflate((-600,)*2),
    ]
    rects[-1].bottomright = space.bottomright
    colors = [
        'gray',
        'gray',
    ]
    neg_colors = [
        'brown',
        'orange',
        'orchid',
        'purple',
        'salmon',
        'teal',
        'tomato',
    ]

    running = True
    while running:
        screen.fill('black')

        for rect, color in zip(rects, colors, strict=True):
            pygame.draw.rect(screen, color, rect, 1)

        for r1, r2 in it.combinations(rects, 2):
            if r1.colliderect(r2):
                result = getattr(r1, op)(r2)
                pygame.draw.rect(screen, 'red', result, fill)

        pygame.display.flip()

        elapsed = clock.tick(framerate)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                else:
                    i = (rect_ops.index(op) + 1) % len(rect_ops)
                    op = rect_ops[i]
                    fill = rect_fills[i]
            elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
                # left button down and moving
                for rect in rects:
                    if rect.collidepoint(event.pos):
                        rect.topleft += pygame.Vector2(event.rel)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('op', choices=rect_ops)
    args = parser.parse_args(argv)
    run(args.op)

if __name__ == '__main__':
    main()
