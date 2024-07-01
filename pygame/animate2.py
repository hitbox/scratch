import math
import os

from collections import deque

import pygamelib

from pygamelib import pygame

class Timer:

    def __init__(self, wrap=1000):
        self.count = 0
        self.wrap = wrap

    def update(self, elapsed):
        self.count = (self.count + elapsed) % self.wrap

    def normalized(self):
        return self.count / self.wrap


def lerp_rects(time, r1, r2):
    x1, y1, w1, h1 = r1
    x2, y2, w2, h2 = r2
    return (
        x1 * (1 - time) + x2 * time,
        y1 * (1 - time) + y2 * time,
        w1 * (1 - time) + w2 * time,
        h1 * (1 - time) + h2 * time,
    )

def ease_in_out_quad(t):
    return t * t * (3 - 2 * t)

def sine_easing(t):
    return (math.sin(math.tau * t) + 1) / 2

def back_ease_out(t):
    p = 1 - t
    return 1 - (p * p * p - p * math.sin(p * math.pi))

def back_ease_in_out(t):
    if t < 0.5:
        p = 2 * t
        return 0.5 * (p * p * p - p * math.sin(p * math.pi))

    p = 1 - (2 * t - 1)
    return  0.5 * (1 - (p * p * p - p * math.sin(p * math.pi))) + 0.5

def bounce_ease_out(t):
    if t < 4 / 11:
        return 121 * t * t / 16
    elif t < 8 / 11:
        return (363 / 40 * t * t) - (99 / 10 * t) + 17 / 5
    elif t < 9 / 10:
        return (4356 / 361 * t * t) - (35442 / 1805 * t) + 16061 / 1805

    return (54 / 5.0 * t * t) - (513 / 25.0 * t) + 268 / 25.0

def bounce_ease_in(t):
    return 1 - bounce_ease_out(1 - t)

def bounce_ease_in_out(t):
    if t < 0.5:
        return 0.5 * bounce_ease_in(t * 2)
    return 0.5 * bounce_ease_out(t * 2 - 1) + 0.5

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        '--frames',
        help = 'Directory containing animation frames.',
    )
    args = parser.parse_args(argv)

    framerate = args.framerate
    window = pygame.Rect((0,0), args.display_size)
    window_frame = window.inflate(-0.10 * window.width, -0.10 * window.height)

    frames = []
    if args.frames:
        filenames = sorted(os.listdir(args.frames))
        paths = (os.path.join(args.frames, fn) for fn in filenames)
        images = list(map(pygame.image.load, paths))
        rects = [image.get_rect() for image in images]
        for rect in rects:
            rect.center = window.center

    rect1 = pygame.Rect(0, 0, 100, 100)
    rect1.bottomright = window_frame.bottomright

    rect2 = pygame.Rect(0, 0, rect1.width * 2, rect1.height * 3)
    rect2.bottomright = window_frame.bottomright

    color1 = pygame.Color('darkorange4')
    color2 = pygame.Color('purple')
    timer = Timer(wrap=2000)

    ease = sine_easing

    clock = pygame.time.Clock()
    fps_queue = deque(maxlen=100)
    elapsed = 0

    font_printer = pygamelib.FontPrinter(pygamelib.monospace_font(20), 'azure')
    screen = pygame.display.set_mode(window.size)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
        # update
        timer.update(elapsed)
        fps_queue.append(clock.get_fps())
        # draw
        screen.fill('black')
        time = timer.normalized()
        eased_time = ease(time)
        color = color1.lerp(color2, time)
        if images:
            index = int(time * len(images)) % len(images)
            image = images[index]
            rect = rects[index]
            screen.blit(image, rect)
        rect = lerp_rects(eased_time, rect1, rect2)
        pygame.draw.rect(screen, color, rect)
        avg_fps = sum(fps_queue) / len(fps_queue)
        lines = [
            f'{avg_fps=:.0f}',
            f'{timer.count=}',
            f'{time=:.04f}',
            f'{eased_time=:.04f}',
        ]
        screen.blit(font_printer(lines), (0,0))
        pygame.display.flip()
        #
        elapsed = clock.tick(framerate)

if __name__ == '__main__':
    main()
