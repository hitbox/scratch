import math

import pygamelib

from pygamelib import pygame

class Circle:

    def __init__(self, center, radius):
        self.center = center
        self.radius = radius


def bobbing(centerables, influences, timeoffsets, amount, time):
    for centerable, influence, timeoffset in zip(centerables, influences, timeoffsets):
        xdelta = math.cos(time + timeoffset) * amount
        ydelta = math.sin(time + timeoffset) * amount
        x, y = centerable.center
        xinfluence, yinfluence = influence
        center = (x + xdelta * xinfluence, y + ydelta * yinfluence)
        centerable.center = center

def rotate(point, angle, center=(0,0)):
    x, y = point
    cx, cy = center

    current = math.atan2(cy - y, cx - x)

    d = math.dist(point, center)
    x = cx + math.sin(current + angle) * d
    y = cy + math.cos(current + angle) * d
    return (x, y)

def circular_engine_shapes(center, radius):
    nacel = Circle(center, radius)
    # nacel_bg
    yield Circle(center, nacel.radius + 2)
    yield nacel
    # intake
    intake = Circle(nacel.center, nacel.radius * 0.60)
    yield intake
    # cone
    yield Circle(nacel.center, intake.radius * 0.25)

def generate_blade(cone, nacel):
    rect = pygame.Rect(
        cone.radius * 1.5, # offset around cone
        -nacel.radius / 16, # centered around zero
        nacel.radius * 2, # length of blade
        nacel.radius / 4 # height of blade
    )
    points = pygamelib.corners(rect)
    yield next(points)
    yield next(points)
    # rounded corner
    cx, cy = rect.midright
    for angle in range(0, 100, 10):
        angle = math.radians(angle)
        x = cx + math.cos(angle) * rect.height / 2
        y = cy + math.sin(angle) * rect.height / 2
        yield (x, y)
    yield from points

def run(display_size, framerate, background):
    window = pygame.Rect((0,0), display_size)
    frame = window.inflate(-200, -200)
    circles = list(circular_engine_shapes(window.center, min(frame.size)/12))
    nacel, _, _, cone = circles
    styles = [
        ('grey10', pygamelib.FILL),
        ('grey30', pygamelib.FILL),
        ('grey10', pygamelib.FILL),
        ('grey50', pygamelib.FILL),
    ]
    bobbing_influences = [
        (0.04, 0.04),
        (0.05, 0.05),
        (0.06, 0.07),
        (0.07, 0.09),
    ]
    timeoffsets = [
        0.0,
        0.0,
        0.1,
        0.2,
    ]

    # object space, right-oriented blade as polygon
    blade = list(generate_blade(cone, nacel))

    blade_animations = []
    for offset in range(30):
        for angle in range(offset, 360 + offset, 30):
            angle = math.radians(angle)
            # produce three blades from angle of first
            anim = []
            for angle_delta in range(0, 360, 360//3):
                angle_delta = math.radians(angle_delta)
                points = [rotate(point, angle + angle_delta) for point in blade]
                anim.append(points)
            blade_animations.append(anim)

    frame = 0
    blade_index = 0
    running = True
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(display_size, vsync=True)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
        # update
        bobbing(circles, bobbing_influences, timeoffsets, amount=3, time=frame * 0.1)
        # draw
        screen.fill(background)
        for circle, (color, width) in zip(circles, styles):
            pygame.draw.circle(screen, color, circle.center, circle.radius, width)

        if (frame % 2) == 0:
            blade_index = (blade_index + 1) % len(blade_animations)
        _blades = blade_animations[blade_index]
        for _blade in _blades:
            points = [pygame.Vector2(cone.center) + point for point in _blade]
            pygame.draw.polygon(screen, 'grey60', points, 0)

        pygame.display.flip()
        elapsed = clock.tick(framerate)
        frame += 1

def main(argv=None):
    parser = pygamelib.command_line_parser()
    args = parser.parse_args(argv)

    run(args.display_size, args.framerate, args.background)

if __name__ == '__main__':
    main()

# 2024-03-31 Sun.
# - watching MATN "The Lamplighters League and the Tower at the End of the World"
# - cutscene swipe transition of old propeller engined plain
# - their's is 3d
# - appears with props spinning until confirm
# - then it moves right and screen wipes right
# - wanted to make something similar from simple shapes
