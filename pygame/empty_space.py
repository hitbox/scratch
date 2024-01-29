import pygamelib

from pygamelib import pygame

UPDATE_RECT_GENERATOR = pygame.event.custom_type()

class Demo(pygamelib.DemoBase):

    def __init__(self, font, inside, rects_generator):
        self.font = font
        self.inside = inside
        self.auto_step = False
        self.rect_renderer = pygamelib.RectRenderer()
        self.rects_generator = rects_generator
        self.reset_rects_generator()

    def reset_rects_generator(self):
        self.rects_generator.reset(self.inside)
        if self.auto_step:
            pygame.time.set_timer(UPDATE_RECT_GENERATOR, 500)

    def do_userevent(self, event):
        if event.type == UPDATE_RECT_GENERATOR:
            if self.rects_generator.is_resolved():
                # disable timer for rect generator
                pygame.time.set_timer(UPDATE_RECT_GENERATOR, 0)
            else:
                self.rects_generator.update()
                pygamelib.post_videoexpose()

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            self.engine.stop()
        elif event.key == pygame.K_RIGHT:
            if not self.rects_generator.is_resolved():
                self.rects_generator.update()
                pygamelib.post_videoexpose()
        else:
            self.rects_generator.reset(self.inside)
            pygamelib.post_videoexpose()

    def do_mousemotion(self, event):
        if event.buttons[0]:
            self.rect_renderer.offset += event.rel
            pygamelib.post_videoexpose()
        elif not any(event.buttons):
            rects = self.rects_generator.rects + self.rects_generator.empties
            for rect in map(pygame.Rect, rects):
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
        self.rect_renderer(self.screen, 'white', 1, self.rects_generator.rects)
        self.rect_renderer(self.screen, 'red', 1, self.rects_generator.empties)
        inside = self.inside.move(self.rect_renderer.offset)

        texts = [
            f'failures={self.rects_generator.failures}',
            f'subdividing={self.rects_generator.subdivide_stack}',
            f'merging={self.rects_generator.merge_stack}',
        ]
        if self.rects_generator.is_resolved():
            texts.append('resolved')
        lines = [self.font.render(text, True, 'white') for text in texts]
        rects = [line.get_rect() for line in lines]
        pygamelib.flow_topbottom(rects)
        pygamelib.move_as_one(rects, bottomleft=self.window.bottomleft)
        for image, rect in zip(lines, rects):
            self.screen.blit(image, rect)
        pygame.display.flip()


def run(display_size, nrects):
    pygame.display.init()
    pygame.font.init()

    window = pygame.Rect((0,)*2, display_size)
    space = window.inflate((-min(window.size)*.25,)*2)
    engine = pygamelib.Engine()
    font = pygame.font.SysFont('monospace', 20)
    rects_generator = pygamelib.RectsGenerator(
        space,
        nrects,
        minwidth=10,
        minheight=10,
    )
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
