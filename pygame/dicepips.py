import random

import pygamelib

from pygamelib import pygame

EVEN_PIP_DELTAS = [
    # (col, row)
    (-1, -1), # topleft
    (-1, +1), # bottomleft
    (-0, -1), # midleft
    (-1, -0), # midtop
]

class CycleDemo(pygamelib.DemoBase):

    def __init__(self, blits, roll_interval):
        self.blits = blits
        self.index = 0
        self.roll = None
        self.timer = None
        self.roll_interval = roll_interval

    def do_quit(self, event):
        self.engine.stop()

    def do_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            pygamelib.post_quit()
        elif event.key in (pygame.K_RIGHT, pygame.K_LEFT):
            if event.key == pygame.K_RIGHT:
                delta = +1
            else:
                delta = -1
            self.index = (self.index + delta) % len(self.blits)
            pygamelib.post_videoexpose()
        elif event.key == pygame.K_SPACE:
            self.roll = random.randint(6, 24)
            self.timer = 0

    def do_videoexpose(self, event):
        self.draw()

    def update(self):
        super().update()
        if self.roll and self.roll > 0:
            if self.timer + self.elapsed >= self.roll_interval:
                self.index = (self.index + random.randint(1, 5)) % len(self.blits)
                self.roll -= 1
                self.timer = (self.timer + self.elapsed) % self.roll_interval
                self.draw()
            else:
                self.timer += self.elapsed

    def draw(self):
        self.screen.fill('black')
        image, rect = self.blits[self.index]
        self.screen.blit(image, rect)
        pygame.display.flip()


def iter_pip_deltas(n):
    """
    Generate the deltas for n number pips.
    """
    if n % 2 != 0:
        # yield center for odd number
        yield (0, 0)
        n -= 1
    for row, col in EVEN_PIP_DELTAS[:n//2]:
        # yield delta and its opposite
        yield (row, col)
        yield (-row, -col)

# 1-9 pip deltas
PIP_DELTAS = {n: list(iter_pip_deltas(n)) for n in range(1,10)}

def iter_rect_ends(rect):
    # generate the dimensional extremes of a rect, its x and y endpoints
    yield (rect.left, rect.right)
    yield (rect.top, rect.bottom)

def remap_delta_xy(rowcol, rect):
    def _remap_dim(item):
        index, rectdim = item
        min_, max_ = rectdim
        return pygamelib.remap(index, -1, +1, min_, max_)
    pos = map(_remap_dim, zip(reversed(rowcol), iter_rect_ends(rect)))
    return tuple(pos)

def make_dicerect(dice_window, rowcol, dice_size, dice_border):
    row, col = rowcol
    # map from delta to screen/rect position
    remap_rect = dice_window.inflate((-(dice_border + dice_size),)*2)
    center = remap_delta_xy(rowcol, remap_rect)
    dice_rect = pygame.Rect(0, 0, dice_size, dice_size)
    dice_rect.center = center
    return dice_rect

def piprect(dice_rect, pipsize, pippos, dice_border):
    """
    Rect for one of the pip positions inside a dice rect.
    """
    pip_width, pip_height = pipsize
    pip_row, pip_col = pippos
    x = pygamelib.remap(
        pip_col,
        -1,
        +1,
        dice_rect.left + dice_border,
        dice_rect.right - pip_width - dice_border,
    )
    y = pygamelib.remap(
        pip_row,
        -1,
        +1,
        dice_rect.top + dice_border,
        dice_rect.bottom - pip_height - dice_border,
    )
    pip_rect = pygame.Rect(x, y, pip_width, pip_height)
    return pip_rect

def draw_pip(surf, rect, border_width, fill_color, border_color):
    center, radius = pygamelib.circle_inside(rect)
    # fill
    pygame.draw.circle(surf, fill_color, center, radius, 0)
    # border
    pygame.draw.circle(surf, border_color, center, radius, 1)

def draw_die(surf, npips, border):
    rect = surf.get_rect()
    pip_size = (
        rect.width // 3 - border,
        rect.height // 3 - border,
    )
    for pippos in PIP_DELTAS[npips]:
        pip_rect = piprect(rect, pip_size, pippos, border)
        draw_pip(surf, pip_rect, border, 'azure', 'indigo')

def run(display_size, roll_interval, dice_size):
    window = pygame.Rect((0,0), display_size)

    blits = []
    for n in range(1,7):
        die_size = (int(min(display_size) * dice_size),)*2
        die_surf = pygame.Surface(die_size)
        die_surf.fill('firebrick')
        border = min(die_size) // 18
        draw_die(die_surf, n, border)
        pygame.draw.rect(die_surf, 'azure', die_surf.get_rect(), border // 2)
        die_rect = die_surf.get_rect(center=window.center)
        blits.append((die_surf, die_rect))

    state = CycleDemo(blits, roll_interval)
    pygame.display.set_mode(display_size)
    engine = pygamelib.Engine()
    engine.run(state)

def main(argv=None):
    """
    Draw dice pips algorithm
    """
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        '--roll-interval',
        type = int,
        default = 200,
        help = 'Milliseconds animation delay for rolling dice.',
    )
    parser.add_argument(
        '--dice-size',
        type = eval,
        default = '0.1',
        help = 'Fraction of window size for dice size.',
    )
    args = parser.parse_args(argv)
    run(args.display_size, args.roll_interval, args.dice_size)

if __name__ == '__main__':
    main()
