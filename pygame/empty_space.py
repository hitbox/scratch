import pygamelib

from pygamelib import pygame

class Demo(pygamelib.DemoBase):

    def __init__(self, font, inside, rects_generator):
        self.font = font
        self.inside = inside
        self.rects_generator = rects_generator
        self.rect_renderer = pygamelib.RectRenderer()
        self.update_rects()

    def update_rects(self):
        self.rects, self.empties = self.rects_generator(self.inside)

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            self.engine.stop()
        else:
            self.update_rects()
            pygamelib.post_videoexpose()

    def do_mousemotion(self, event):
        if event.buttons[0]:
            self.rect_renderer.offset += event.rel
            pygamelib.post_videoexpose()
        elif not any(event.buttons):
            for rect in self.rects + self.empties:
                if rect.collidepoint(event.pos):
                    self.rect_renderer.highlight = rect
                    break
            else:
                self.rect_renderer.highlight = None
            pygamelib.post_videoexpose()

    def do_videoexpose(self, event):
        self.draw()

    def draw(self):
        self.screen.fill('black')
        self.rect_renderer(self.screen, 'white', 0, self.rects)
        self.rect_renderer(self.screen, 'red', 1, self.empties)
        for index, rect in enumerate(self.rects):
            pygame.draw.circle(self.screen, 'limegreen', rect.center, 5, 0)
            label = self.font.render(str(index), True, 'brown')
            rect = label.get_rect(center=rect.center)
            rect.clamp_ip(self.inside)
            self.screen.blit(label, rect)
        pygame.display.flip()


def run(display_size, nrects):
    pygame.font.init()
    window = pygame.Rect((0,)*2, display_size)
    space = window.inflate((-min(window.size)*.25,)*2)
    engine = pygamelib.Engine()
    font = pygame.font.SysFont('monospace', 24)
    rects_generator = pygamelib.RectsGenerator(nrects, minwidth=10, minheight=10)
    state = Demo(font, space, rects_generator)
    pygame.display.set_mode(window.size)
    engine.run(state)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument('--nrects', type=int, default=1)
    args = parser.parse_args(argv)
    run(args.display_size, args.nrects)

if __name__ == '__main__':
    main()
