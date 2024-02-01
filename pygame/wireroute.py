import itertools as it

import pygamelib

from pygamelib import pygame

class LineRectsDemo(pygamelib.DemoBase):

    def __init__(self, rects, line_start):
        self.rects = rects
        self.line_start = line_start
        self._intersects = set()

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        pygamelib.post_quit()

    def do_mousemotion(self, event):
        pygamelib.post_videoexpose()

    def do_videoexpose(self, event):
        self.draw()

    def update(self):
        super().update()
        self._intersects.clear()
        line = (self.line_start, pygame.mouse.get_pos())
        for rect in self.rects:
            for intersection in pygamelib.line_rect_intersections(line, rect):
                self._intersects.add(intersection)

    def draw(self):
        self.screen.fill('black')
        self.draw_rects()
        self.draw_line()
        self.draw_intersects()
        pygame.display.flip()

    def draw_rects(self):
        for rect in self.rects:
            pygame.draw.rect(self.screen, 'azure', rect, 1)

    def draw_line(self):
        pygame.draw.line(
            self.screen,
            'mediumorchid',
            self.line_start,
            pygame.mouse.get_pos()
        )

    def draw_intersects(self):

        def distance_from_start(point):
            return pygame.Vector2(point).distance_to(self.line_start)

        points = sorted(self._intersects, key=distance_from_start)
        items = zip(points, it.chain(['magenta'], it.repeat('red')))
        for point, color in items:
            pygame.draw.circle(self.screen, color, point, 4)


def make_rects(frame, thickness):
    frame_quads = list(map(pygame.Rect, pygamelib.rectquadrants(frame)))
    rects = []
    # top left horizontal wall
    rects.append(
        pygame.Rect(frame.topleft, (frame.width * 0.20, thickness))
    )
    # top right horizontal wall
    rects.append(
        pygame.Rect(
            rects[-1].right + thickness,
            rects[-1].top,
            frame.right - rects[-1].right - thickness,
            thickness
        )
    )
    # left wall
    rects.append(
        pygame.Rect(
            frame.left,
            rects[0].bottom,
            thickness,
            frame.height - rects[0].height - thickness,
        )
    )
    # right wall
    rects.append(
        pygame.Rect(
            frame.right - thickness,
            rects[0].bottom,
            thickness,
            rects[2].height, # left wall height
        )
    )
    # top left inner box
    box = pygamelib.make_rect(
        size = pygame.Vector2(frame.size) * 0.20,
    )
    rects.append(
        pygame.Rect(
            pygamelib.make_rect(
                box,
                center = frame_quads[0].center,
            )
        )
    )
    # center inner box
    rects.append(
        pygame.Rect(
            pygamelib.make_rect(
                box,
                center = frame.center,
            )
        )
    )
    # bottom right inner box
    rects.append(
        pygame.Rect(
            pygamelib.make_rect(
                box,
                center = frame_quads[2].center,
            )
        )
    )
    # bottom left wall
    rects.append(
        pygame.Rect(
            pygamelib.make_rect(
                rects[1], # top right horizontal wall
                bottomleft = frame.bottomleft,
            )
        )
    )
    # bottom right wall
    rects.append(
        pygame.Rect(
            pygamelib.make_rect(
                rects[0], # top left horizontal wall
                bottomright = frame.bottomright,
            )
        )
    )
    return rects

def run_linerect(display_size):
    frame = pygame.Rect((0,)*2, display_size)
    frame.inflate_ip((-min(display_size)*0.5,)*2)
    thickness = min(frame.size) / 8
    rects = make_rects(frame, thickness)
    line_start = (
        rects[-2].right + (rects[-1].left - rects[-2].right) / 2,
        rects[-1].bottom + thickness,
    )
    state = LineRectsDemo(rects, line_start)
    pygame.display.set_mode(display_size)
    engine = pygamelib.Engine()
    engine.run(state)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument('demo', choices=['linerect'], default='linerect')
    args = parser.parse_args(argv)

    if args.demo == 'linerect':
        run_linerect(args.display_size)

if __name__ == '__main__':
    main()

# 2024-02-01
# - dated late
# - wanted to make a system where you can wrap a "wire" around rects.
# /home/hitbox/repos/reference/iacore/wire-routing-game
# https://www.jeffreythompson.org/collision-detection/line-line.php
# https://git.envs.net/iacore/wire-routing-game
# https://www.1a-insec.net/blog/31-wire-routing-input-scheme/
