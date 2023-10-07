import argparse
import contextlib
import itertools as it
import math
import os

from collections import deque
from operator import attrgetter

right_angle = math.pi / 2

with open(os.devnull, 'w') as devnull:
    with contextlib.redirect_stdout(devnull):
        import pygame

del devnull

_color = 'olive'
_rect = pygame.Rect(100, 100, 200, 300)
_points = [_rect.topleft, _rect.topright, _rect.bottomright, _rect.bottomleft]

def draw_rect(screen):
    pygame.draw.rect(screen, _color, _rect)

def draw_polygon(screen):
    pygame.draw.polygon(screen, _color, _points)

def demo(draw):
    """
    Compare average framerate between drawing with rect or polygon.
    """
    # 2023-10-01
    # - rect is slightly slower! polygon averages 30-ish frames faster.
    pygame.font.init()
    screen = pygame.display.set_mode((800,)*2)
    window = screen.get_rect()
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('monospace', 30)

    duration = 5000

    fps_list = deque(maxlen=duration)

    def average_fps():
        return sum(fps_list) / len(fps_list)

    elapsed = 0
    running = True
    while running:
        elapsed += clock.tick()
        fps_list.append(clock.get_fps())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
        screen.fill('black')
        draw(screen)
        image = font.render(f'{average_fps():07.2f}', True, 'white')
        screen.blit(image, image.get_rect(midbottom=window.midbottom))
        pygame.display.flip()
        if elapsed > duration:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    if fps_list:
        print(f'final avg. fps: {average_fps():07.2f}')

def main(argv=None):
    """
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('draw_type', choices=['draw_rect', 'draw_polygon'])
    args = parser.parse_args(argv)
    draw = eval(args.draw_type)
    demo(draw)

if __name__ == '__main__':
    main()
