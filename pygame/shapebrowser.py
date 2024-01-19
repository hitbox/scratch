import argparse

import pygamelib

from pygamelib import pygame

class ShapeBrowser(pygamelib.BrowseBase):

    def __init__(self, font, scale, offset, shapes):
        self.font = font
        self.scale = scale
        self.offset = pygame.Vector2(offset)
        self._shapes = shapes
        self.update_shapes_scale()

    def update_shapes_scale(self):
        self.shapes = [shape.scale(self.scale) for shape in self._shapes]

    def do_videoexpose(self, event):
        self.draw()

    def do_mousewheel(self, event):
        if 0 < self.scale + event.y < 1000:
            self.scale += event.y
            self.update_shapes_scale()
            pygamelib.post_videoexpose()

    def draw(self):
        self.screen.fill('black')
        for shape in self.shapes:
            shape.draw(self.screen, self.offset)
        text = self.font.render(f'{self.scale}', True, 'white')
        rect = text.get_rect()
        self.screen.blit(text, rect)

        text = self.font.render(f'{self.offset}', True, 'white')
        rect = text.get_rect(topleft=rect.bottomleft)
        self.screen.blit(text, rect)
        pygame.display.flip()


def run(screen_size, shapes, scale, offset):
    pygame.font.init()
    font = pygame.font.SysFont('monospace', 20)
    editor = ShapeBrowser(font, scale, offset, shapes)
    engine = pygamelib.Engine()
    pygame.display.set_mode(screen_size)
    engine.run(editor)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'shapes',
        type = argparse.FileType(),
    )
    parser.add_argument(
        '--scale',
        type = int,
        default = 1,
        help = 'Scale shapes',
    )
    parser.add_argument(
        '--screen-size',
        type = pygamelib.sizetype(),
        default = '800',
    )
    parser.add_argument(
        '--offset',
        type = pygamelib.sizetype(),
        default = '0',
    )
    args = parser.parse_args(argv)

    if args.shapes:
        shape_parser = pygamelib.ShapeParser()
        shapes = list(shape_parser.parse_file(args.shapes))
    else:
        shapes = None

    run(args.screen_size, shapes, args.scale, args.offset)

if __name__ == '__main__':
    main()
