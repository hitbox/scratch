import os
import argparse
import inspect

from contextlib import redirect_stdout
from enum import Enum
from types import SimpleNamespace

with redirect_stdout(open(os.devnull, 'w')):
    import pygame

class Base:

    def move(self, delta):
        for name in dir(self):
            if not name.startswith('_'):
                setattr(self, name, getattr(self, name) + delta)


class Steer(Base):

    def __init__(self, point, angle):
        self.point = point
        self.angle = angle

    def __str__(self):
        return f'point: {self.point}, angle: {self.angle}'


class Truck(Base):

    def __init__(self, steer, drive_point, hitch_point):
        self.steer = steer
        self.drive_point = drive_point
        self.hitch_point = hitch_point
        self.steer_distance = self.steer.point.distance_to(self.drive_point)
        self.hitch_distance = self.hitch_point.distance_to(self.drive_point)
        # Calculate wheelbase (distance between drive and steer)
        self.wheelbase = self.steer.point.distance_to(self.drive_point)

    def move(self, delta):
        self.steer.point += delta
        self.drive_point += delta
        self.hitch_point += delta

    @property
    def truck_direction(self):
        # Current truck direction
        return (self.steer.point - self.drive_point).normalize()

    def forward(self, magnitude):
        # Move drive point forward in current direction
        drive_amount = self.truck_direction * magnitude
        self.drive_point += drive_amount
        self.hitch_point += drive_amount
        # Move the steer point in the steering direction by the same amount.
        self.steer.point += pygame.Vector2(drive_amount, 0).rotate(self.steer_angle)


class Trailer(Base):

    def __init__(self, front_point, hitch_point, trail_point):
        self.front_point = front_point
        self.hitch_point = hitch_point
        self.trail_point = trail_point

    def move(self, delta):
        self.front_point += delta
        self.hitch_point += delta
        self.trail_point += delta


def argument_parser():
    parser = argparse.ArgumentParser()
    return parser

def main(argv=None):
    parser = argument_parser()
    args = parser.parse_args(argv)

    pygame.font.init()

    engine = SimpleNamespace(
        screen = pygame.display.set_mode((512, 512)),
        clock = pygame.time.Clock(),
        framerate = 60,
        font = pygame.font.SysFont(None, 25),
    )
    engine.frame = engine.screen.get_rect()

    truck = Truck(
        steer = Steer(
            point = pygame.Vector2(10, 0),
            angle = 180,
        ),
        drive_point = pygame.Vector2(20, 0),
        hitch_point = pygame.Vector2(30, 0),
    )
    delta = (206, 206)
    truck.move(delta)

    trailer = Trailer(
        front_point = pygame.Vector2(20, 0),
        hitch_point = pygame.Vector2(30, 0),
        trail_point = pygame.Vector2(60, 0),
    )
    trailer.move(delta)
    turn_amount = 5
    drive_amount = 0.05

    elapsed = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_UP]:
            truck.forward(drive_amount)
        if pressed[pygame.K_DOWN]:
            truck.forward(-drive_amount)
        truck.steer_angle = truck.truck_direction.angle_to((0,0))
        if pressed[pygame.K_LEFT]:
            truck.steer_angle = -turn_amount
        if pressed[pygame.K_RIGHT]:
            truck.steer_angle = turn_amount

        engine.screen.fill('black')
        text_images = []
        for name in dir(truck):
            if not name.startswith('_'):
                value = getattr(truck, name)
                if not inspect.ismethod(value):
                    image = engine.font.render(f'{name}: {value}', True, 'white')
                    text_images.append(image)

        text_rects = [image.get_rect() for image in text_images]
        for r1, r2 in zip(text_rects, text_rects[1:]):
            r2.topleft = r1.bottomleft

        for image, rect in zip(text_images, text_rects):
            engine.screen.blit(image, rect)

        pygame.draw.line(engine.screen, 'azure', truck.steer.point, truck.drive_point, 1)
        pygame.draw.circle(engine.screen, 'yellow', truck.steer.point, 10)
        pygame.draw.line(engine.screen, 'brown', trailer.front_point, trailer.trail_point, 1)
        pygame.display.update()
        elapsed = engine.clock.tick(engine.framerate)

if __name__ == '__main__':
    main()
