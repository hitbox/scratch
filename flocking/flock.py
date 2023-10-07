import pygame
from pygame.locals import *
import random
import os
import sys
import math
from pprint import pprint as pp

def dotproduct(v1, v2):
    # v1x * v2x + v1y * v2y
    return (v1[0] * v2[0]) + (v1[1] * v2[1])

def length(v):
    return math.sqrt(v[0] ** 2 + v[1] ** 2)

def normalize(v):
    l = length(v)
    return (v[0] / l, v[1] / l)

def between_angle(v1, v2):
    dotp = dotproduct(v1, v2)
    q = length(v1) * length(v2)
    return math.acos(dotp / q)

class Boid(object):

    def __init__(self, (x, y), angle, speed=0.0, color="red"):
        self.x = float(x)
        self.y = float(y)
        self.angle = angle
        self.speed = speed
        self.color = color
        self._font = pygame.font.Font(None, 14)
        self._anglefmt = "angle: {:03.1f}".format
        self._debug = False

    @property
    def position(self):
        return (self.x, self.y)

    def update(self, center_mass_position):
        # our "vector position"
        x1 = self.x
        y1 = self.y

        x2, y2 = center_mass_position

        dx = x2 - x1
        dy = y2 - y1

        dist = math.sqrt(dx * dx + dy * dy)
        self.dist = dist

        angle_between = (math.atan2(dy, dx) - self.angle) % (math.pi * 2)
        self.angle_between = angle_between

        #view_angle = self.view_angle = math.radians(dist / 2)
        view_angle = self.view_angle = math.radians(5)
        if math.fabs(angle_between) > view_angle:
            turn_angle = self.turn_angle = math.copysign(math.radians(10), angle_between)
            self.angle = (self.angle + turn_angle) % (math.pi * 2)

        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

    def draw(self, surface):
        x2 = self.x + math.cos(self.angle) * (self.speed * 7)
        y2 = self.y + math.sin(self.angle) * (self.speed * 7)
        pygame.draw.line(surface, pygame.Color(self.color),
                                  (int(self.x), int(self.y)), 
                                  (int(x2),     int(y2)))

        textsurfs = []
        textrects = []
        for attr in "angle angle_between view_angle dist turn_angle".split():
            if hasattr(self, attr):
                if 'angle' in attr:
                    value = math.degrees(getattr(self, attr))
                else:
                    value = getattr(self, attr)
                text = "{}: {:.2f}".format(attr, value)
                textsurf = self._font.render(text, True, Color("white"))
                textsurfs.append(textsurf)
                #
                textrect = textsurf.get_rect()
                try:
                    textrect.top = textrects[-1].bottom
                except IndexError:
                    pass
                textrects.append(textrect)

        if textrects:
            textrect = textrects[0].unionall(textrects[1:])
            textsurf = pygame.Surface(textrect.size, flags=SRCALPHA)

            textrect.topleft = int(self.x), int(self.y)
            textrect = textrect.clamp(surface.get_rect())

            for surf, rect in zip(textsurfs, textrects):
                textsurf.blit(surf, rect.topleft)

            surface.blit(textsurf, textrect)


def main():

    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.display.init()
    pygame.font.init()
    screen = pygame.display.set_mode((640, 480))
    world = screen.get_rect()
    clock = pygame.time.Clock()

    def RandomBoid():
        x = random.randint(world.left, world.right)
        y = random.randint(world.top, world.bottom)
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(0.5, 2)
        boid = Boid((x, y), angle, speed)
        return boid

    def draw():
        screen.fill((0,0,0))
        pygame.draw.circle(screen, Color("red"), world.center, 10, 1)
        for boid in boids:
            boid.draw(screen)
        pygame.display.flip()

    updateindex = 0
    nblast = 5
    boids = [RandomBoid() for _ in xrange(nblast)]
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
                    boids = [RandomBoid() for _ in xrange(nblast)]
        updateindex = (updateindex + 1) % 12
        if updateindex == 0:
            # filter out boids who've gone out of this world
            boids = [ boid for boid in boids if world.collidepoint(boid.position) ]
            # update the boids
            center_mass_position = world.center
            for boid in boids:
                boid.update(center_mass_position)
        draw()

if __name__ == '__main__':
    main()

