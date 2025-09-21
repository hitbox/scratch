import argparse
import logging
import os
import random

from contextlib import redirect_stdout

with redirect_stdout(open(os.devnull, 'w')):
    import pygame

logger = logging.getLogger('userinterface')

class Rect(pygame.Rect):

    def update_from(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self

    def lerp(self, b, time):
        tx, ty = time
        x = lerp(self.left, b.right - self.width, tx)
        y = lerp(self.top, b.bottom - self.height, ty)
        return self.__class__(x, y, self.width, self.height)

    def invlerp(self, container):
        max_x = container.right - self.width
        max_y = container.bottom - self.height

        tx = invlerp(container.left, max_x, self.x)
        ty = invlerp(container.top, max_y, self.y)

        return (tx, ty)


class Spawn:

    def __init__(self, rect, func=None):
        self.rect = rect
        self._func = func

    @property
    def func(self):
        if self._func is None:
            return random.randint
        return self._func

    def generate_points(self, n):
        func = self.func
        for _ in range(n):
            x = func(self.rect.left, self.rect.right)
            y = func(self.rect.top, self.rect.bottom)
            yield (x, y)


class Sprite:

    def __init__(self, image, rect=None):
        self.image = image
        if rect is None:
            rect = self.image.get_rect()
        self.rect = Rect(rect)

    @classmethod
    def debug_from_point(cls, point, size):
        image = pygame.Surface(size)
        rect = Rect(image.get_rect(topleft=point))
        return cls(image, rect)


class MiniMap:

    def __init__(self, container, cursor):
        self.container = container
        self.cursor = cursor

    def invlerp(self):
        left = self.container.left
        right = self.container.right - self.cursor.width
        top = self.container.top
        bottom = self.container.bottom - self.cursor.height

        tx = invlerp(left, right, self.cursor.x)
        ty = invlerp(top, bottom, self.cursor.y)

        return (tx, ty)


class Drag:

    def __init__(self):
        self.rects = []
        self.target = None

    def update_from_position(self, pos):
        for rect in self.rects:
            if rect.collidepoint(pos):
                self.target = rect
                break


def get_bounding(rects):
    xs, ys, widths, heights = zip(*rects)
    x = min(xs)
    y = min(ys)
    r = max(x + w for x, w in zip(xs, widths))
    b = max(y + h for y, h in zip(ys, heights))
    return (x, y, r - x, b - y)

def lerp(a, b, t):
    """
    Position between a and b, at time t.
    """
    return a + t * (b - a)

def invlerp(a, b, x):
    """
    Time of x between a and b.
    """
    if a == b:
        return 0
    return (x - a) / (b - a)

def create_sprites(window, font):
    spawn_scale = 16
    spawn = Spawn(window.inflate(window.width * spawn_scale, window.height * spawn_scale))
    sprites = []
    size = (128, 32)
    background = 'grey5'
    for point in spawn.generate_points(5_000):
        sprite = Sprite.debug_from_point(point, size)
        sprite.image.fill(background)
        sprites.append(sprite)

        text_image = font.render(f'{point}', True, 'white')
        norm_rect = sprite.image.get_rect()
        sprite.image.blit(text_image, text_image.get_rect(center=norm_rect.center))
        pygame.draw.rect(sprite.image, 'grey10', norm_rect, 1)
    return sprites

def run_minimap():
    screen = pygame.display.set_mode((800,800))
    window = Rect(screen.get_rect())
    clock = pygame.time.Clock()
    framerate = 60
    camera = Rect(window)
    pygame.font.init()
    font = pygame.font.Font(size=20)

    sprites = create_sprites(window, font)
    bounding = Rect(get_bounding([sprite.rect for sprite in sprites]))

    mini_map = MiniMap(window, Rect(0,0,30,30).update_from(center=window.center))

    drag = Drag()
    drag.rects.append(mini_map.cursor)

    step = 1
    key_move = {
        pygame.K_UP: (0, -step),
        pygame.K_RIGHT: (+step, 0),
        pygame.K_DOWN: (0, +step),
        pygame.K_LEFT: (-step, 0),
    }

    update_camera = False
    elapsed = 0
    running = True
    while running:
        # Events
        for event in pygame.event.get():
            logger.info(event)
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in key_move:
                    dx, dy = key_move[event.key]
                    mini_map.cursor.move_ip(dx, dy)
                    update_camera = True
            elif event.type == pygame.MOUSEMOTION:
                button_left, button_middle, button_right = event.buttons
                if button_left and drag.target:
                    # Left click drag objects.
                    drag.target.move_ip(event.rel[0] * step, event.rel[1] * step)
                    if drag.target is mini_map.cursor:
                        drag.target.clamp_ip(mini_map.container)
                        update_camera = True

                elif button_middle:
                    # Middle click drag camera.
                    dx = event.rel[0] * step
                    dy = event.rel[1] * step
                    camera.move_ip(dx, dy)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    drag.update_from_position(event.pos)

        if update_camera:
            tx, ty = mini_map.invlerp()
            camera.x = lerp(bounding.left, bounding.right - camera.width, tx)
            camera.y = lerp(bounding.top, bounding.bottom - camera.height, ty)
            update_camera = False

        # Draw
        screen.fill('black')
        pygame.draw.rect(screen, 'white', mini_map.container, 1)
        pygame.draw.rect(screen, 'red', mini_map.cursor, 0)
        visible = [sprite for sprite in sprites if sprite.rect.colliderect(camera)]
        for sprite in visible:
            screen.blit(sprite.image, sprite.rect.move(-camera.x, -camera.y))

        pygame.display.flip()
        elapsed = clock.tick(framerate)

def argument_parser():
    parser = argparse.ArgumentParser()
    
    levels = list(logging.getLevelNamesMapping().keys())
    parser.add_argument(
        '--level',
        choices = levels,
    )

    parser.add_argument(
        '--seed',
        type = int,
    )
    return parser

def main(argv=None):
    parser = argument_parser()
    args = parser.parse_args(argv)

    if args.level:
        logging.basicConfig(level=getattr(logging, args.level))

    if isinstance(args.seed, int):
        random.seed(args.seed)

    run_minimap()

if __name__ == '__main__':
    main()
