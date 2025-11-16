import argparse
import contextlib
import itertools as it
import math
import operator
import os

from collections import deque
from functools import partial
from types import SimpleNamespace

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

class assets:

    def __init__(self, basepath, scale=1):
        self.basepath = basepath
        self.scale = scale
        self.cache = {}

    def image(self, filename):
        if filename not in self.cache:
            image = pygame.image.load(os.path.join(self.basepath, filename))
            if self.scale != 1:
                size = image.get_size()
                scaled = apply(operator.mul, self.scale, size)
                image = pygame.transform.scale(image, scaled)
            self.cache[filename] = image
        return self.cache[filename]

    def rect(self, filename):
        return self.image(filename).get_rect()


class sizetype:

    def __init__(self, separator=',', type=int, duplicate_size=2):
        self.separator = separator
        self.type = type
        self.duplicate_size = duplicate_size

    def __call__(self, string):
        size = tuple(map(int, string.replace(',', ' ').split()))
        while len(size) < self.duplicate_size:
            size += size
        return size


class RectFill:

    def __init__(self, color):
        self.color = color

    def draw(self, surf, rect):
        pygame.draw.rect(surf, self.color, rect, 0)


class RectBorder:

    def __init__(self, color, size=1):
        self.color = color
        self.size = size

    def draw(self, surf, rect):
        pygame.draw.rect(surf, self.color, rect, self.size)


class RectImageBorder:

    def __init__(self, vertical, horizontal, topleft_corner):
        self.vertical = vertical
        self.horizontal = horizontal
        self.topleft_corner = topleft_corner
        self.topright_corner = pygame.transform.flip(topleft_corner, 1, 0)
        self.bottomleft_corner = pygame.transform.flip(topleft_corner, 0, 1)
        self.bottomright_corner = pygame.transform.flip(topleft_corner, 1, 1)

    @classmethod
    def slice_image(cls, image, thickness):
        corner = slice_image(image, pygame.Rect((0,0), (thickness, thickness)))
        vertical = slice_image(image, pygame.Rect((thickness,0), (thickness, thickness)))
        horizontal = slice_image(image, pygame.Rect((0,thickness), (thickness, thickness)))
        return cls(vertical, horizontal, corner)

    def draw(self, surf, rect):
        width_step = self.horizontal.get_rect().width
        height_step = self.vertical.get_rect().height
        # Draw corners
        surf.blit(self.topleft_corner, rect)
        surf.blit(self.topright_corner, copyat(rect, topright=rect.topright))
        surf.blit(self.bottomleft_corner, copyat(rect, bottomleft=rect.bottomleft))
        surf.blit(self.bottomright_corner, copyat(rect, bottomright=rect.bottomright))
        # Draw top and bottom
        for x in range(rect.left + width_step, rect.right, width_step):
            surf.blit(self.vertical, (x, rect.top))
            surf.blit(self.vertical, (x, rect.bottom - height_step))
        # Draw left and right
        for y in range(rect.top, rect.bottom, height_step):
            surf.blit(self.horizontal, (rect.left, y))
            surf.blit(self.horizontal, (rect.right - width_step, y))


def slice_image(source, rect):
    new = pygame.Surface(rect.size, flags=pygame.SRCALPHA)
    new.blit(source, (0,0), rect)
    return new

def copyat(rect, **kwargs):
    new = rect.copy()
    for key, val in kwargs.items():
        setattr(new, key, val)
    return new

class RectStyle:

    def __init__(self, fill=None, border=None):
        self.fill = fill
        self.border = border

    def draw(self, surf, rect):
        if self.fill:
            self.fill.draw(surf, rect)
        if self.border:
            self.border.draw(surf, rect)


class ResizeStyle:

    def __init__(self, color, spacing=4, direction='topright-bottomleft'):
        self.color = color
        self.spacing = spacing
        self.direction = direction

    def draw(self, surf, rect):
        for start, end in diagonal_lines(rect, spacing=self.spacing, direction=self.direction):
            pygame.draw.line(surf, self.color, start, end, 1)


class CloseStyle:

    def __init__(self, color):
        self.color = color

    def draw(self, surf, rect):
        pygame.draw.line(surf, self.color, rect.topleft, rect.bottomright, 1)
        pygame.draw.line(surf, self.color, rect.topright, rect.bottomleft, 1)


class ImageStyle:

    def __init__(self, image):
        self.image = image

    @classmethod
    def from_path(cls, filename):
        image = pygame.image.load(filename)
        return cls(image=image)

    def draw(self, surf, rect):
        surf.blit(self.image, rect)


class WindowStyle:

    def __init__(self, frame, title, resize, border, close):
        self.frame = frame
        self.title = title
        self.resize = resize
        self.border = border
        self.close = close

    def draw(self, surf, window):
        self.frame.draw(surf, window.frame)
        self.title.draw(surf, window.titlebar)
        self.resize.draw(surf, window.resizebar)
        self.border.draw(surf, window.frame)
        self.close.draw(surf, window.closebutton)


class Window:

    def __init__(self, size, closebutton=None):
        self.frame = pygame.Rect((0,0), size)
        self.titlebar = self.frame.copy()
        self.titlebar.height = min(10, self.titlebar.height * 0.2)
        self.resizebar = self.frame.copy()
        self.resizebar.height = min(10, self.resizebar.height * 0.2)
        self.resizebar.width = min(10, self.resizebar.width * 0.2)
        self.resizebar.bottomright = self.frame.bottomright
        if closebutton is None:
            closebutton = pygame.Rect(0, 0, 10, 10)
        self.closebutton = closebutton
        self.closebutton.topright = self.frame.topright

    def move(self, rel):
        self.frame.move_ip(rel)
        self.titlebar.move_ip(rel)
        self.resizebar.bottomright = self.frame.bottomright
        self.closebutton.topright = self.frame.topright

    def resize(self, rel):
        self.frame.width += rel[0]
        self.frame.height += rel[1]
        self.titlebar.width = self.frame.width
        self.resizebar.bottomright = self.frame.bottomright
        self.closebutton.topright = self.frame.topright


class Display:

    def __init__(self, size, scale=1):
        self.size = size
        self.scale = scale
        self.buffer = pygame.Surface(self.size)
        self.windowsize = tuple(dim * self.scale for dim in self.size)

    def clear(self):
        self.buffer.fill('black')

    def init(self):
        self.window = pygame.display.set_mode(self.windowsize)

    def update(self):
        pygame.transform.scale(self.buffer, self.windowsize, self.window)
        pygame.display.update()


class WindowManager:

    def __init__(self, windows, styles, scale=1):
        self.windows = windows
        self.styles = styles
        self.scale = scale
        self.dragging = None
        self.hovering = None
        self.resizing = None
        self.closing = None

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.handle_mousemotion(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mousebuttondown(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = None
            self.resizing = None

    def lift_top(self, window, style):
        self.windows.remove(window)
        self.windows.append(window)
        self.styles.remove(style)
        self.styles.append(style)

    def handle_mousebuttondown(self, event):
        pos = apply(operator.truediv, self.scale, event.pos)
        for window, style in zip(self.windows, self.styles):
            if window.closebutton.collidepoint(pos):
                window.particle = Particle(window.frame.topleft, (0,0), (0,1))
                self.closing = window
                break
            elif window.titlebar.collidepoint(pos):
                self.dragging = window
                self.lift_top(window, style)
                break
            elif window.resizebar.collidepoint(pos):
                self.resizing = window
                self.lift_top(window, style)
                break
        else:
            self.hovering = None
            self.resizing = None

    def handle_mousemotion(self, event):
        if self.dragging:
            rel = apply(operator.truediv, self.scale, event.rel)
            self.dragging.move(rel)
        elif self.resizing:
            rel = apply(operator.truediv, self.scale, event.rel)
            self.resizing.resize(rel)

    def update(self, elapsed):
        if self.closing:
            self.closing.particle.update(elapsed)
            rel = self.closing.particle.position - self.closing.frame.topleft
            self.closing.move(rel)


class Particle:

    def __init__(self, position, velocity, acceleration):
        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(velocity)
        self.acceleration = pygame.Vector2(acceleration)

    def update(self, elapsed):
        self.velocity += self.acceleration
        self.position += self.velocity


def diagonal_lines(rect, spacing=10, direction='topleft-bottomright'):
    """
    Draw parallel diagonal lines inside a rect at the slope of its corners.

    :param rect: pygame.Rect to fill with lines
    :param spacing: distance between parallel lines
    :param direction: 'topleft-bottomright' or 'topright-bottomleft'
    """
    diagonal = math.sqrt(rect.width**2 + rect.height**2)
    if direction == 'topleft-bottomright':
        # Lines go from top-left to bottom-right (positive slope)
        # We'll start lines from the left edge and top edge

        # Calculate the diagonal length to know how many lines we need

        # Start from top-left corner, move perpendicular to the diagonal
        # The perpendicular direction for positive slope diagonal
        perp_angle = math.atan2(rect.height, rect.width) + math.pi/2
        dx = math.cos(perp_angle) * spacing
        dy = math.sin(perp_angle) * spacing

        # Generate starting points along the perpendicular
        num_lines = int(diagonal / spacing) + 2

        for i in range(-num_lines, num_lines):
            # Start point moves perpendicular to diagonal
            start_x = rect.left + i * dx
            start_y = rect.top + i * dy

            # End point is along the diagonal direction
            end_x = start_x + rect.width
            end_y = start_y + rect.height

            # Clip line to rectangle bounds
            if clip_line_to_rect(start_x, start_y, end_x, end_y, rect):
                start, end = clip_line_to_rect(start_x, start_y, end_x, end_y, rect)
                yield (start, end)

    else:
        # topright-bottomleft
        perp_angle = math.atan2(rect.height, -rect.width) + math.pi/2
        dx = math.cos(perp_angle) * spacing
        dy = math.sin(perp_angle) * spacing

        num_lines = int(diagonal / spacing) + 2

        for i in range(-num_lines, num_lines):
            start_x = rect.right + i * dx
            start_y = rect.top + i * dy

            end_x = start_x - rect.width
            end_y = start_y + rect.height

            if clip_line_to_rect(start_x, start_y, end_x, end_y, rect):
                start, end = clip_line_to_rect(start_x, start_y, end_x, end_y, rect)
                yield (start, end)

def clip_line_to_rect(x1, y1, x2, y2, rect):
    """
    Clip a line to rectangle bounds using Cohen-Sutherland algorithm.
    Returns tuple of (start_point, end_point) or None if line is outside rect.
    """
    # Region codes
    INSIDE = 0  # 0000
    LEFT = 1    # 0001
    RIGHT = 2   # 0010
    BOTTOM = 4  # 0100
    TOP = 8     # 1000

    def compute_code(x, y):
        code = INSIDE
        if x < rect.left:
            code |= LEFT
        elif x > rect.right:
            code |= RIGHT
        if y < rect.top:
            code |= TOP
        elif y > rect.bottom:
            code |= BOTTOM
        return code

    code1 = compute_code(x1, y1)
    code2 = compute_code(x2, y2)

    while True:
        # Both points inside
        if code1 == 0 and code2 == 0:
            return ((int(x1), int(y1)), (int(x2), int(y2)))

        # Both points outside in same region
        if code1 & code2 != 0:
            return None

        # At least one point outside, clip it
        code_out = code1 if code1 != 0 else code2

        # Find intersection point
        if code_out & TOP:
            x = x1 + (x2 - x1) * (rect.top - y1) / (y2 - y1)
            y = rect.top
        elif code_out & BOTTOM:
            x = x1 + (x2 - x1) * (rect.bottom - y1) / (y2 - y1)
            y = rect.bottom
        elif code_out & RIGHT:
            y = y1 + (y2 - y1) * (rect.right - x1) / (x2 - x1)
            x = rect.right
        elif code_out & LEFT:
            y = y1 + (y2 - y1) * (rect.left - x1) / (x2 - x1)
            x = rect.left

        # Update point and code
        if code_out == code1:
            x1, y1 = x, y
            code1 = compute_code(x1, y1)
        else:
            x2, y2 = x, y
            code2 = compute_code(x2, y2)

def get_rect(*args, **kwargs):
    """
    :param *args:
        Optional rect used as base. Otherwise new (0,)*4 rect is created.
    :param kwargs:
        Keyword arguments to set on new rect.
    """
    if not len(args) in (0, 1):
        raise ValueError()
    if len(args) == 1:
        result = args[0].copy()
    else:
        result = pygame.Rect(0,0,0,0)
    for key, val in kwargs.items():
        setattr(result, key, val)
    return result

def apply(op, value, container):
    class_ = type(container)
    return class_(op(dim, value) for dim in container)

def simple_sprite(rect, color):
    image = pygame.Surface(rect.size)
    image.fill(color)
    return SimpleNamespace(
        image = image,
        rect = rect,
    )

def cli():
    """
    Inventory
    """
    # saw this:
    # https://www.reddit.com/r/pygame/comments/xasi84/inventorycrafting_system/
    # TODO:
    # [X] Like Resident Evil 4 in 2d
    # [X] grab / drop
    # [ ] Auto arrange with drag+drop animations
    # [X] Rotate items
    # [ ] Stacking?
    # [ ] Combine to new item?
    # [ ] Stealing minigame. Something chases or attacks your cursor.
    # [ ] Moving through items are a way of jumping, could be part of gameplay.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--size',
        default = '400,400',
        type = sizetype(),
        help = 'Screen size. Default: %(default)s',
    )
    parser.add_argument(
        '--scale',
        default = 2,
        type = int,
        help = 'Screen size. Default: %(default)s',
    )
    parser.add_argument(
        '--output',
        help = 'Format string for frame output.',
    )
    args = parser.parse_args()
    display = Display(args.size, args.scale)
    display.init()

    clock = pygame.time.Clock()
    framerate = 60

    pygame.font.init()

    kenney_game_assets = assets(
        basepath = os.path.expanduser(
            '~/Downloads/Kenney Game Assets/Kenney Game Assets All-in-1 3.1.0'
            '/UI assets/UI Pack/PNG/Grey/Default/'
        ),
        scale = 2,
    )

    image_style = WindowStyle(
        frame = RectFill(color='black'),
        title = RectFill(color='grey'),
        resize = ResizeStyle(color='grey', spacing=2),
        border = RectImageBorder.slice_image(
            kenney_game_assets.image('button_square_depth_border.png'),
            thickness = 10,
        ),
        close = ImageStyle(
            image = kenney_game_assets.image('icon_outline_cross.png'),
        ),
    )

    color1_style = WindowStyle(
        frame = RectFill(color='yellow'),
        title = RectFill(color='red'),
        resize = ResizeStyle(color='red', spacing=2),
        border = RectBorder(color='red'),
        close = CloseStyle(color='purple'),
    )

    wm = WindowManager([
            Window(
                size = (200, 300),
                closebutton = kenney_game_assets.rect('icon_cross.png'),
            ),
        ],
        styles = [
            image_style,
        ],
        scale = args.scale,
    )

    running = True
    elapsed = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
            wm.handle_event(event)
        wm.update(elapsed)
        display.clear()
        for window, style in zip(wm.windows, wm.styles):
            if window is wm.hovering:
                color = 'yellow'
            else:
                color = 'red'
            style.draw(display.buffer, window)

        display.update()
        elapsed = clock.tick(framerate)

if __name__ == '__main__':
    cli()
