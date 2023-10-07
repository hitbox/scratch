import pygame
from pygame.locals import *
import random
import os
import sys
import math

def main():
    """This is to help get a grip on what the angles atan2 is returning mean
    """
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.display.init()
    screen = pygame.display.set_mode((256, 240))
    world = screen.get_rect()
    clock = pygame.time.Clock()

    running = True
    while running:
        elapsed = clock.tick(60)
        #
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_q:
                    pygame.event.post(pygame.event.Event(QUIT))
                elif event.key == K_SPACE:
                    boids.extend(RandomBoid() for _ in xrange(nblast))

        x1, y1 = world.center
        x2, y2 = pygame.mouse.get_pos()
        screen.fill(Color("black"))
        pygame.draw.line(screen, Color("white"), (x1, y1), (x2, y2))

        dx = float(x2) - x1
        dy = float(y2) - y1

        angle = math.degrees(math.atan2(dy, dx))

        text = "dx:{:03.2f} dy:{:03.2f} a:{:03.2f}".format(dx, dy, angle)
        pygame.display.set_caption(text)
        pygame.display.flip()

if __name__ == '__main__':
    main()

