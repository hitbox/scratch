import itertools as it
import math

import pygamelib

from pygamelib import pygame

def circle_point(center, size_or_diameter, angle):
    cx, cy = center
    if isinstance(size_or_diameter, (list, tuple)):
        rx, ry = size_or_diameter
        rx /= 2
        ry /= 2
    else:
        rx = ry = size_or_diameter / 2
    x = cx + rx * math.cos(angle)
    y = cy + ry * math.sin(angle)
    return (x, y)

def circle_points(center, size_or_radius, angle1=0, angle2=360, step=15):
    for angle in map(math.radians, range(angle1, angle2+step, step)):
        yield circle_point(center, size_or_radius, angle)

def normrange(start, stop=None, step=1):
    if stop is None:
        stop = start
        start = 0
    while start < stop:
        yield start / (stop - step)
        start += step

def smoothstep(t):
    return t * t * (3 - 2*t)

def render_polygon(poly, color, width):
    x, y, w, h = pygamelib.rect_from_points(poly)
    image = pygame.Surface((w+4, h+4))
    points = list((_x - x + 1, _y - y + 1) for _x, _y in poly)
    pygame.draw.polygon(image, color, points, width)
    return image

def run(display_size, framerate, background, every, n, d, color):
    window = pygamelib.make_rect(size=display_size)

    bounding = pygamelib.reduce_rect(window, -0.5)

    final_radius = min(bounding.size)

    delay_frames = n // d
    inner_radii_fractions = (
        list(it.repeat(0, delay_frames))
        + list(map(smoothstep, normrange(n - delay_frames)))
    )
    outer_radii_fractions = list(map(smoothstep, normrange(n)))

    explosion_frames = [
        list(
            it.chain(
                circle_points(bounding.center, inner_t * final_radius, step=5),
                circle_points(bounding.center, outer_t * final_radius, step=5),
            )
        )
        for inner_t, outer_t in zip(inner_radii_fractions, outer_radii_fractions)
    ]

    images = [render_polygon(polygon, color, 0) for polygon in explosion_frames]
    rects = [image.get_rect(center=bounding.center) for image in images]
    blits = it.cycle(zip(images, rects))

    clock = pygame.time.Clock()
    font = pygamelib.monospace_font(20)
    frame = 0
    elapsed = 0
    running = True
    screen = pygame.display.set_mode(window.size)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
        screen.fill(background)
        if frame == 0 or frame % every == 0:
            blitable = next(blits)
        screen.blit(*blitable)
        image = font.render(f'{clock.get_fps():.0f}', True, 'white')
        screen.blit(image, (0,0))
        pygame.display.flip()
        elapsed = clock.tick(framerate)
        frame += 1

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        'every',
        type = int,
        help = 'Next frame every %(dest)s frames.',
    )
    parser.add_argument(
        'frames',
        type = int,
        help = 'Total number of frames.',
    )
    parser.add_argument(
        'delay_denom',
        type = int,
        help = 'frames / delay_denom for the trailing, inner circle',
    )
    parser.add_argument(
        'color',
    )
    args = parser.parse_args(argv)
    run(
        args.display_size,
        args.framerate,
        args.background,
        args.every,
        args.frames,
        args.delay_denom,
        args.color,
    )

if __name__ == '__main__':
    main()

# 2024-04-08 Mon.
# - Exploding circle thing like here:
# https://css-tricks.com/wp-content/uploads/2016/06/web_heart_animation.png
#   where one circle "explodes" and, later, another inner circle "explodes"
#   giving a shockwave impression
# - Thinking about Flask style decorators for hooks into the main loop.
# 2024-03-25 Tue.
# - Something that looks interesting (long):
# https://www.andreinc.net/2024/04/24/from-the-circle-to-epicycles
