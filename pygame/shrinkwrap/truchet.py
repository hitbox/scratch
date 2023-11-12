import argparse
import random
import time

from collections import deque
from itertools import combinations

import rectop
import render.truchet
import render.text

from lib.external import pygame

DEBUGCOLOR = (200,30,200)
BGCOLOR = (0,)*3
BGCOLOR2 = (10,)*3

FGCOLOR = (200,)*3
FGCOLOR2 = (230,)*3

def loop():
    pygame.font.init()

    window = pygame.display.set_mode((6*155,)*2)
    frame = window.get_rect()
    gui_frame = frame.inflate(-frame.width*0.20,-frame.height*0.20)
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    population = rectop.MIDPOINTS + [None]
    midpoint_combinations = list(combinations(population, 2))
    fps_list = deque(maxlen=60*10)
    draw_crosshairs = True

    connections = None
    def next_connections():
        """
        Randomly generate a list of curve connections.
        """
        nonlocal connections
        k = random.randint(1, len(midpoint_combinations)//2)
        connections = random.sample(midpoint_combinations, k)

    truchet_image = None
    truchet_rect = None
    connections_image = None
    connections_rect = None
    def next_truchet_image():
        """
        Generate the truchet image from connectors.
        """
        nonlocal truchet_image
        nonlocal truchet_rect
        nonlocal connections_image
        nonlocal connections_rect
        truchet_image = render.truchet.tile(
            midpoints_radius = min(frame.size) // (6*6),
            corners_radius = min(frame.size) // (6*1),
            connections = connections
        )
        truchet_rect = truchet_image.get_rect(center=frame.center)
        #
        connections_strings = [f'{left} -> {right}' for left, right in connections]
        connections_image = render.text.lines(
            font,
            antialias = True,
            color = FGCOLOR,
            lines = connections_strings,
            surface_flags = pygame.SRCALPHA
        )
        connections_rect = connections_image.get_rect(topright=gui_frame.topright)

    def do_tick():
        clock.tick()
        fps_list.append(clock.get_fps())

    def do_events():
        nonlocal running
        nonlocal draw_crosshairs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Q to quit
                if event.key in (pygame.K_q,):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                # spacebar to move to next
                elif event.key in (pygame.K_SPACE,):
                    next_connections()
                    next_truchet_image()
                # S to toggle crosshairs
                elif event.key in (pygame.K_s,):
                    draw_crosshairs = not draw_crosshairs

    def do_draw():
        window.fill(BGCOLOR)
        # truchet tile image
        window.blit(truchet_image, truchet_rect)
        # connector names
        window.blit(connections_image, connections_rect)
        # FPS
        avg_fps = sum(fps_list) / len(fps_list)
        fps_image = font.render(f'{avg_fps:,.0f}', True, FGCOLOR)
        window.blit(fps_image, fps_image.get_rect(bottomright=gui_frame.bottomright))
        # crosshairs at mouse
        if draw_crosshairs:
            mx, my = pygame.mouse.get_pos()
            pygame.draw.line(window, DEBUGCOLOR, (frame.left, my), (frame.right, my))
            pygame.draw.line(window, DEBUGCOLOR, (mx, frame.top), (mx, frame.bottom))
        # update
        pygame.display.flip()

    next_connections()
    next_truchet_image()
    running = True
    while running:
        do_tick()
        do_events()
        do_draw()

def main(argv=None):
    """
    Truchet tile drawing demo.
    """
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)
    loop()

#https://christophercarlson.com/portfolio/multi-scale-truchet-patterns/

if __name__ == '__main__':
    main()
