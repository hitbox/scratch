import argparse
import contextlib
import math
import os
import turtle

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

class KochSnowflake:

    def __init__(self, left, right, forward):
        self.left = left
        self.right = right
        self.forward = forward

    def subloop(self, length, i=1):
        if i == 0:
            self.forward(length)
        else:
            self.subloop(length/3, i-1)
            self.left(60)
            self.subloop(length/3, i-1)
            self.right(120)
            self.subloop(length/3, i-1)
            self.left(60)
            self.subloop(length/3, i-1)

    def loop(self, length):
        for i in range(3):
            self.subloop(length, i=3)
            self.right(120)


class Cursor:

    def __init__(self, position=(0,0), angle=0, points=None):
        self.position = pygame.Vector2(position)
        self.angle = angle
        if points is None:
            points = []
        self.points = points

    def commit(self):
        self.points.append(self.position.copy())

    def left(self, angle):
        self.angle += -angle

    def right(self, angle):
        self.angle += angle

    def forward(self, length):
        self.commit()
        other = pygame.Vector2.from_polar((length, self.angle))
        self.position += other


def wrap_points(points):
    xs, ys = zip(*points)
    left = min(xs)
    top = min(ys)
    right = max(xs)
    bottom = max(ys)
    width = right - left
    height = bottom - top
    return pygame.Rect(left, top, width, height)

def wrap_rects(rects):
    return pygame.Rect((0,)*4).unionall(rects)

def run_turtle():
    turtle.color('red')
    koch_snowflake = KochSnowflake(turtle.left, turtle.right, turtle.forward)
    koch_snowflake.loop(500)

def run_pygame():
    pygame.font.init()
    screen = pygame.display.set_mode((800,)*2)
    frame = screen.get_rect()
    clock = pygame.time.Clock()
    framerate = 60
    font = pygame.font.SysFont('monospace', 20)

    cursor = Cursor()
    koch_snowflake = KochSnowflake(cursor.left, cursor.right, cursor.forward)
    koch_snowflake.loop(300)
    cursor.points.append(cursor.points[0].copy())

    # center the snow flake
    points_wrapped = wrap_points(cursor.points)
    delta = pygame.Vector2(frame.center) - points_wrapped.center
    for point in cursor.points:
        point += delta

    n = 0
    running = True
    while running:
        elapsed = clock.tick(framerate)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
        # update
        # NOTE
        # - n is a length not an index, so don't "wrap" until +1
        n = (n + 1) % (len(cursor.points) + 1)

        # draw
        screen.fill('black')
        points = cursor.points[:n]
        if len(points) > 1:
            pygame.draw.lines(screen, 'azure', False, points)

        lines = [
            'Escape/Q to quit',
            f'{clock.get_fps():.2f} FPS',
        ]
        images = [font.render(line, True, 'azure') for line in lines]
        rects = [image.get_rect() for image in images]
        for r1, r2 in zip(rects, rects[1:]):
            r2.topright = r1.bottomright
        wrapped = wrap_rects(rects)
        delta = pygame.Vector2(frame.bottomright) - wrapped.bottomright
        for rect in rects:
            rect.topleft += delta
        for image, rect in zip(images, rects):
            screen.blit(image, rect)

        pygame.display.flip()

def main(argv=None):
    """
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['turtle', 'pygame'])
    args = parser.parse_args(argv)
    if args.command == 'turtle':
        run_turtle()
    elif args.command == 'pygame':
        run_pygame()

if __name__ == '__main__':
    main()

# 2023-11-06
# https://compileralchemy.substack.com/p/cursing-and-re-cursing-what-if-we
# https://en.wikipedia.org/wiki/Weierstrass_function
