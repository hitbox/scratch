import itertools as it
import random

import pygamelib

from pygamelib import pygame

rect_ops = ['clip', 'union', 'contiguous']

class Demo(pygamelib.DemoBase):
    """
    Demonstrate some rect operations. Move rects with left click drag. Copy on
    right click.
    """

    def __init__(self, rects, rect_operation):
        self.rects = rects
        self.rect_operation = rect_operation
        self.dragging = None
        self.offset = pygame.Vector2()
        self.result = None

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            self.engine.stop()

    def do_mousebuttondown(self, event):
        if event.button not in (pygame.BUTTON_LEFT, pygame.BUTTON_RIGHT):
            return
        for rect in self.rects:
            if rect.move(self.offset).collidepoint(event.pos):
                if event.button == pygame.BUTTON_LEFT:
                    self.dragging = rect
                else:
                    newrect = rect.copy()
                    newrect.x = random.randint(
                        self.window.left,
                        self.window.right - newrect.width
                    )
                    newrect.y = random.randint(
                        self.window.top,
                        self.window.bottom - newrect.height,
                    )
                    self.rects.append(newrect)
                pygamelib.post_videoexpose()
                break
        else:
            self.dragging = None

    def do_mousemotion(self, event):
        if self.dragging:
            self.dragging.move_ip(event.rel)
            self.update_result()
            pygamelib.post_videoexpose()
        elif event.buttons[0]:
            self.dragging = None
            self.offset += event.rel
            pygamelib.post_videoexpose()

    def do_mousebuttonup(self, event):
        self.dragging = None

    def do_videoexpose(self, event):
        self.draw()

    def update_result(self):
        for r1, r2 in it.combinations(self.rects, 2):
            if hasattr(r1, self.rect_operation):
                opfunc = getattr(r1, self.rect_operation)
                self.result = [opfunc(r2)]
            elif self.rect_operation == 'contiguous':
                rects = pygamelib.generate_contiguous(self.rects)
                self.result = sorted(rects, key=pygamelib.area, reverse=True)
            else:
                opfunc = getattr(pygamelib, self.rect_operation)
                self.result = [pygame.Rect(opfunc(r1, r2))]

    def draw(self):
        self.screen.fill('black')
        for rect in self.rects:
            pygame.draw.rect(self.screen, 'white', rect.move(self.offset), 1)
        if self.result:
            colors = map(pygame.Color, pygamelib.UNIQUE_THECOLORS.values())
            colors = filter(lambda c: c.hsla[1] == 100, colors)
            colors = sorted(colors, key=lambda c: c.hsla[0])
            for rect, color in zip(self.result, colors):
                rect = pygame.Rect(rect).move(self.offset)
                pygame.draw.rect(self.screen, color, rect, 1)
        pygame.display.flip()


def run(display_size, rect_operation):
    window = pygame.Rect((0,)*2, display_size)
    panels = list(map(pygame.Rect, pygamelib.rectquadrants(window)))

    rect_a = pygamelib.reduce(window, 0.70)
    rect_b = rect_a.copy()

    rect_a.center = panels[0].center
    rect_b.center = panels[1].center

    demo = Demo([rect_a, rect_b], rect_operation)
    pygame.display.set_mode(display_size)
    engine = pygamelib.Engine()
    engine.run(demo)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument('op', choices=rect_ops)
    args = parser.parse_args(argv)
    run(args.display_size, args.op)

if __name__ == '__main__':
    main()
