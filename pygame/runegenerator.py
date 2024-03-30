import itertools as it
import random

from fractions import Fraction

import pygamelib

from pygamelib import pygame

origin = (0, ) * 2

class relative_index:
    """
    Callable returning the relative index normalized to -1 and +1.
    """

    def __init__(self, indexable, index):
        self.indexable = indexable
        self.index = index

    def __call__(self, item):
        d = self.indexable.index(item) - self.index
        if d < 0:
            return -1
        elif d > 0:
            return +1


class RectModel:

    def __init__(
        self,
        display_size,
        fractions_size,
        gui_inflate = (-100,)*2,
    ):
        self.window = pygame.Rect(origin, display_size)
        self.gui = self.window.inflate(*gui_inflate)

        # "window" of generated points
        self.points = pygame.Rect(origin, fractions_size)
        self.points.midright = self.gui.midright

        # "window" of list of fraction items
        self.list_view = pygame.Rect(
            origin,
            (self.gui.width, self.gui.height * 0.75)
        )
        self.list_view.midleft = self.gui.midleft


def divrect(rect, *fractions):
    x, y, w, h = rect
    for wportion, hportion in fractions:
        yield (x + w * wportion, y + h * hportion)

def diagify(values):
    return zip(*it.repeat(values, 2))

def gridify(values):
    return it.product(*it.repeat(values, 2))

def range_over(denom):
    """
    Generate ratios with denominator over range between one and denominator.
    -> 1/denom, 2/denom, ..., (n-1)/denom
    """
    for numerator in range(1, denom):
        yield numerator / denom

def generate_fraction_items(ndenoms, start=2):
    """
    Generate pairs (denominator, tuple(1/d, 2/d, 3/d, ..., (ndenom-1)/d))
    """
    denoms_and_ratios = tuple(
        (denom, tuple(range_over(denom)))
        for denom in range(start, ndenoms)
    )

    # pairs of ratios of each dimension
    for pair in it.product(denoms_and_ratios, repeat=2):
        denoms, ratios = zip(*pair)
        name = '_'.join(map(str, denoms))
        # NOTES
        # - intention is to just repeat the last ratio to fill
        fillvalue = ratios[-1][-1]
        item = (f'diag_{name}', tuple(it.zip_longest(*ratios, fillvalue=fillvalue)))
        yield item

    # ratios as grids of points
    for denom, ratios in denoms_and_ratios:
        item = (f'grid_{denom}', tuple(gridify(ratios)))
        yield item

def before_after_index(indexable, index):
    grouped = it.groupby(indexable, key=relative_index(indexable, index))
    grouped = {key: tuple(group) for key, group in grouped}
    # above/before
    yield grouped.get(-1, tuple())
    # below/after
    yield grouped.get(+1, tuple())

def flow_outward_from_index(current_index, current_rect, item_rects):
    above, below = before_after_index(item_rects, current_index)

    last = current_rect
    for rect in reversed(above):
        rect.bottomleft = last.topleft
        last = rect

    last = current_rect
    for rect in below:
        rect.topleft = last.bottomleft
        last = rect

def flow_for_listbox(
    item_rects,
    list_view,
    current_index,
    current_rect,
):
    # position current item rect
    current_rect.clamp_ip(list_view)
    flow_outward_from_index(current_index, current_rect, item_rects)
    # move all rects so that the current is visible
    if not list_view.contains(current_rect):
        moved = current_rect.copy()
        moved.midleft = list_view.midleft
        delta = pygame.Vector2(moved.topleft) - current_rect.topleft
        for _rect in item_rects:
            _rect.topleft += delta

def get_listbox_data(
    fraction_images,
    list_view,
    current_index
):
    # NOTES
    # - there will be many equal rects generated
    # - assign y so that when we .index we find unique indexes
    # - otherwise .index find the first by equality
    item_rects = tuple(image.get_rect(y=y) for y, image in enumerate(fraction_images))

    index_rect = item_rects[current_index]
    flow_for_listbox(item_rects, list_view, current_index, index_rect)

    bg_rect = (index_rect.x, index_rect.y, list_view.width, index_rect.height)

    current_portion = current_index/(len(fraction_images)-1)
    visible_rects = tuple(filter(list_view.contains, item_rects))
    portion_visible = len(visible_rects) / len(fraction_images)

    if portion_visible < 1:
        scrollbar_bg = pygame.Rect(0, 0, 20, list_view.height)
        scrollbar_bg.midleft = list_view.midright
        scrollbar_btn = pygame.Rect(
            (scrollbar_bg.x, 0),
            (20, scrollbar_bg.height * portion_visible)
        )
        scrollbar_range = scrollbar_bg.height - scrollbar_btn.height
        scrollbar_btn.y = scrollbar_bg.y + scrollbar_range * current_portion
    else:
        scrollbar_btn = None

    data = dict(
        bg_rect = bg_rect,
        item_rects = item_rects,
        scrollbar_btn = scrollbar_btn,
        list_view = list_view,
    )
    return data

def render_listbox_with_scrollbar(
    screen,
    listbox_data,
    fraction_images,
):
    """
    render list of options with current highlighted
    """
    list_view = listbox_data['list_view']
    # draw frame
    pygame.draw.rect(screen, 'grey20', list_view, 1)
    # selected item background
    pygame.draw.rect(screen, 'grey20', listbox_data['bg_rect'], 0)
    items = [
        (image, rect)
        for image, rect in zip(fraction_images, listbox_data['item_rects'])
        if list_view.contains(rect)
    ]
    screen.blits(items)
    if listbox_data['scrollbar_btn']:
        pygame.draw.rect(screen, 'grey50', listbox_data['scrollbar_btn'], 0)

def run(display_size, framerate, background, rect_size):
    fractions = tuple(generate_fraction_items(16))

    rectdb = RectModel(display_size, rect_size)
    points_container = tuple(
        tuple(divrect(rectdb.points, *fracs))
        for _, fracs in fractions
    )
    current = 0
    points = points_container[current]

    running = True
    clock = pygame.time.Clock()
    font = pygamelib.monospace_font(20)

    fraction_images = tuple(
        font.render(name, True, 'white') for name, _ in fractions
    )
    rectdb.list_view.width = 20 + max(image.get_width() for image in fraction_images)
    listbox_data = get_listbox_data(fraction_images, rectdb.list_view, current)

    screen = pygame.display.set_mode(display_size)
    pygame.key.set_repeat(200, 20)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
                elif event.key in (pygame.K_UP, pygame.K_DOWN):
                    if event.key == pygame.K_UP:
                        delta = -1
                    else:
                        delta = +1
                    current = (current + delta) % len(fractions)
                    points = points_container[current]
                    listbox_data = get_listbox_data(fraction_images, rectdb.list_view, current)
        screen.fill(background)
        # render
        pygame.draw.rect(screen, 'brown', rectdb.points, 1)
        for point in points:
            pygame.draw.circle(screen, 'red', point, 4, 1)
        render_listbox_with_scrollbar(screen, listbox_data, fraction_images)
        pygame.display.flip()
        elapsed = clock.tick(framerate)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        'rect_size',
        type = pygamelib.sizetype(),
        help = 'Size of rect.',
    )
    args = parser.parse_args(argv)

    run(args.display_size, args.framerate, args.background, args.rect_size)

if __name__ == '__main__':
    main()

# 2024-03-30 Sat.
# Rune Generator
# Like runes in Kenny Game Assets
# /home/hitbox/Downloads/Kenney Game Assets All-in-1 2.1.0/Rune Pack/
# - random points
# - random pick pairs
# - random or sorted ways of drawing lines between pairs

