import argparse
import contextlib
import math
import os

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

class Line:

    def __init__(self, start=None, end=None, color=None):
        if start is None:
            start = (0, 0)
        self.start = start
        if end is None:
            end = (0, 0)
        self.end = end
        if color is None:
            color = 'magenta'
        self.color = color

    def __iter__(self):
        return iter([self.start, self.end])


class Camera:

    def __init__(self, size):
        self.view = pygame.Rect((0, 0), size)
        self.position = pygame.Vector2(self.view.center)
        self.velocity = pygame.Vector2()
        x = -min(size) // 2
        self.focus = self.view.inflate(x, x)
        self.focus.center = self.position
        # TODO
        # - trying to make the focus rect appear on screen where it should.

    def to_world(self, point):
        return self.position + point

    def to_screen(self, point):
        return point - self.position

    def focus_as_screen(self):
        return self.focus.move(*-self.position)

    def update(self, elapsed):
        self.position += self.velocity
        self.view.center = self.position
        self.focus.center = self.position


class EventMixin:

    def dispatch_event(self, event):
        eventname = pygame.event.event_name(event.type)
        handlername = f'on_{eventname.lower()}'
        handler = getattr(self, handlername, None)
        if handler:
            handler(event)


class RectSprite:

    def __init__(self, size, color):
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.position = pygame.Vector2(self.rect.topleft)

    def update(self):
        self.rect.topleft = self.position


class DemoData:

    def __init__(self):
        self.player = RectSprite((32,)*2, 'red')
        self.lines = []
        self.newline_start = None


class DemoScene(EventMixin):

    def __init__(self):
        pygame.mouse.set_visible(False)
        self.screen = pygame.display.get_surface()
        self.window = self.screen.get_rect()
        self.clock = pygame.time.Clock()
        self.frames_per_second = 60
        self.camera = Camera(self.window.size)
        self.ui_font = pygame.font.SysFont('monospace', 14)
        self.data = DemoData()

    def on_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def on_mousebuttondown(self, event):
        if event.button == pygame.BUTTON_LEFT:
            # start drawing line
            self.data.newline_start = self.camera.to_world(event.pos)

    def on_mousebuttonup(self, event):
        if event.button == pygame.BUTTON_LEFT:
            # finish drawing line
            end = self.camera.to_world(event.pos)
            line = Line(self.data.newline_start, end, 'darkolivegreen')
            self.data.lines.append(line)
            self.data.newline_start = None

    def on_mousemotion(self, event):
        button_left, button_middle, button_right = event.buttons
        if button_right:
            # move camera
            self.camera.position -= event.rel

    def lines_to_draw(self):
        lines = self.data.lines[:]
        if self.data.newline_start:
            mouse_pos = pygame.mouse.get_pos()
            preview = Line(
                self.data.newline_start,
                self.camera.to_world(mouse_pos),
                'white'
            )
            lines.append(preview)
        return lines

    def update(self):
        # update state and draw
        elapsed = self.clock.tick(self.frames_per_second)
        mouse_pos = pygame.mouse.get_pos()
        self.camera.update(elapsed)
        # draw
        self.screen.fill('black')
        # draw player
        player = self.data.player
        pos = -pygame.Vector2(self.camera.view.topleft)
        self.screen.blit(player.image, player.rect.move(*pos))
        # draw lines
        for line in self.lines_to_draw():
            points = map(self.camera.to_screen, line)
            pygame.draw.line(self.screen, line.color, *points)
        # draw camera
        pygame.draw.rect(self.screen, 'magenta', self.camera.focus_as_screen(), 1)
        # draw ui
        cam = self.camera
        text_lines = [
            f'{cam.view=}',
            f'{cam.focus=}',
            f'{cam.position=}',
        ]
        images = [self.ui_font.render(line, True, 'azure') for line in text_lines]
        rects = list(map(pygame.Surface.get_rect, images))
        rects[0].bottomright = self.window.bottomright
        setpairattr(rects, 'bottomright', 'topright')
        for image, rect in zip(images, rects):
            self.screen.blit(image, rect)
        # draw cursor
        pygame.draw.circle(self.screen, 'azure', mouse_pos, 5, 2)
        pygame.display.flip()


def setpairattr(items, sattr, gattr):
    for i1, i2 in zip(items, items[1:]):
        setattr(i2, sattr, getattr(i1, gattr))

def run(scene):
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                scene.dispatch_event(event)
        scene.update()

def main(argv=None):
    """
    """
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

    pygame.display.set_mode((512,)*2)
    pygame.font.init()

    scene = DemoScene()
    run(scene)

if __name__ == '__main__':
    main()

# 2023-10-08
# - rewatched Many A True Nerd's one-off of Webbed
# - watching "Carrot Helper" playthrough of Webbed.
# - felt like making simple camera, with player and ability to draw lines
