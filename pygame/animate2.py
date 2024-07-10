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


def bezier(t, p0, p1, p2, p3):
    """
    Compute the Bezier value at time t using control points p0, p1, p2, p3.
    """
    t_squared = t*t
    t_cubed = t*t*t
    u = 1 - t
    u_squared = u*u
    u_cubed = u*u*u
    x = (u_cubed * p0[0]
         + 3 * u_squared * t * p1[0]
         + 3 * u * t_squared * p2[0]
         + t_cubed * p3[0])
    y = (u_cubed * p0[1]
         + 3 * u_squared * t * p1[1]
         + 3 * u * t_squared * p2[1]
         + t_cubed * p3[1])
    return (x, y)

def ease_in_out(t):
    p0 = (0.0, 0.0)
    p1 = (0.5 - 0.2, 0.0 - 1)
    p2 = (0.5 + 0.2, 1.0 + 1)
    p3 = (1.0, 1.0)
    x, y = bezier(t, p0, p1, p2, p3)
    return y

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

def parametric(t, alpha=2):
    t_squared = t * t
    return  t_squared / (alpha * (t_squared - t) + 1)

def run_original(args):
    framerate = args.framerate
    window = pygame.Rect((0,0), args.display_size)
    window_frame = window.inflate(-0.10 * window.width, -0.10 * window.height)

    frames = []
    if not args.frames:
        images = None
    else:
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
    fps_queue = deque(maxlen=1_000_000)
    elapsed = 0

    font = pygamelib.monospace_font(20)
    font_printer = pygamelib.FontPrinter(font, 'azure')
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
        frame_fps = clock.get_fps()
        fps_queue.append(frame_fps)
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
            f'{frame_fps=:.0f}',
            f'{avg_fps=:.0f}',
            f'{timer.count=}',
            f'{time=:.04f}',
            f'{eased_time=:.04f}',
        ]
        screen.blit(font_printer(lines), (0,0))
        pygame.display.flip()
        #
        elapsed = clock.tick(framerate)

def run_rect_grid(args):
    framerate = args.framerate
    window = pygame.Rect((0,0), args.display_size)

    window_frame = window.inflate(-0.10 * window.width, -0.10 * window.height)
    graph_frame = window_frame.copy()
    graph_surf = pygame.Surface(graph_frame.size, pygame.SRCALPHA)

    nx = 1
    ny = 1
    rect_width = window_frame.width // nx
    rect_height = window_frame.height // ny
    xs = list(range(window_frame.x, window_frame.right, rect_width))
    ys = list(range(window_frame.y, window_frame.bottom, rect_height))
    rects = [pygame.Rect(x, y, 0, 0) for x in xs for y in ys]

    clock = pygame.time.Clock()
    time = Timer(wrap=2000)

    def _get_time():
        return sine_easing(time.normalized())

    screen = pygame.display.set_mode(window.size)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
        screen.fill('black')
        _time = _get_time()
        # update rect sizes and draw
        for rect in rects:
            rect.width = pygamelib.lerp(_time, 0, rect_width)
            rect.height = pygamelib.lerp(_time, 0, rect_height)
            _rect = rect.copy()
            _rect.normalize()
            pygame.draw.rect(screen, 'darkorange4', _rect, 0)
            pygame.draw.rect(screen, 'darkred', _rect, 1)
        # draw time graph
        # TODO
        # - fix plot coming out linear
        # - also need bigger surface to plot past zero and one
        graph_x = pygamelib.lerp(_time, graph_frame.left, graph_frame.right)
        graph_y = pygamelib.lerp(_time, graph_frame.bottom, graph_frame.top)
        pygame.draw.circle(graph_surf, 'darkgreen', (graph_x, graph_y), 5)
        screen.blit(graph_surf, graph_frame)
        pygame.display.flip()
        # update clock and timer
        elapsed = clock.tick(framerate)
        time.update(elapsed)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        '--frames',
        help = 'Directory containing animation frames.',
    )
    args = parser.parse_args(argv)
    run_rect_grid(args)

if __name__ == '__main__':
    main()
