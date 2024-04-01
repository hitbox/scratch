import itertools as it
import string

from fractions import Fraction

import pygamelib

from pygamelib import pygame

class ListData:

    def __init__(self, items, current=0):
        self.items = items
        self.current = current

    def move(self, delta):
        self.current = (self.current + delta) % len(self.items)

    def next(self):
        self.move(+1)

    def previous(self):
        self.move(-1)

    def current_proportion(self):
        return self.current / (len(self.items) - 1)


class VProportionalLayout:

    def __init__(self, frame):
        self.frame = frame

    def __call__(self, inner, p):
        """
        Update position of inner rect, inside this frame.
        """
        inner.top = self.frame.y + (self.frame.height - inner.height) * p


class ListRenderer:

    def __init__(self, draw_selected, draw_frame, blitter):
        self.draw_selected = draw_selected
        self.draw_frame = draw_frame
        self.blitter = blitter

    def contained_items(self, frame, images, rects):
        for image, rect in zip(images, rects):
            if frame.contains(rect):
                yield (image, rect)

    def __call__(self, surf, rects, current, images, frame):
        self.draw_frame(surf, frame)
        items = self.contained_items(frame, images, rects)
        for image, rect in items:
            if rect is current:
                self.draw_selected(surf, rect)
            self.blitter(surf, image, rect)


def run(display_size, framerate, background, list_data, nshow):
    # NOTES
    # - lots of interdepedence between frame and list rects
    # Layout Process
    #  1. create images for list_data items.
    #  2. create rects from images.
    #  3. create and position a frame from item rects.
    #  4. position first item rect against frame vertically.
    # 5a. set item rects' x position and width against frame.
    # 5b. flow items rects down from first.

    window = pygame.Rect((0,0), display_size)
    font = pygamelib.monospace_font(20)

    list_images = [font.render(text, True, 'white') for text in list_data.items]
    list_rects = [image.get_rect() for image in list_images]

    frame = pygame.Rect(pygamelib.wrap(list_rects))
    frame.width *= 1.50
    frame.height = nshow * min(rect.height for rect in list_rects)
    frame.center = window.center

    list_rects[0].top = frame.top
    for rectpair in it.pairwise(list_rects):
        for _rect in rectpair:
            _rect.left = frame.left + 2
            _rect.width = frame.width
        r1, r2 = rectpair
        r2.top = r1.bottom

    list_renderer = ListRenderer(
        draw_selected = pygamelib.RectRenderer(
            # background of selected item
            color = 'grey30',
            width = pygamelib.FILL,
        ),
        draw_frame = pygamelib.RectRenderer(
            color = ('grey20', 'grey10', 'grey20', 'grey10'),
            width = 1,
        ),
        blitter = pygamelib.blit,
    )

    scroll_frame = pygame.Rect(
        pygamelib.make_rect(
            frame,
            width = 20,
            topleft = frame.topright,
        )
    )

    def scroll_button_proportion():
        visible = tuple(rect for rect in list_rects if frame.colliderect(rect))
        return len(visible) / len(list_rects)

    scroll_button = pygame.Rect(
        pygamelib.make_rect(
            scroll_frame,
            height = scroll_button_proportion() * scroll_frame.height,
        )
    )
    scroll_button_layout = VProportionalLayout(scroll_frame)
    scroll_frame_renderer = pygamelib.RectRenderer(
        color = ('white', 'grey20', 'grey30', 'grey10'),
        width = pygamelib.FILL,
    )
    scroll_button_renderer = pygamelib.RectRenderer(
        color = 'grey30',
        width = pygamelib.FILL,
    )

    current_rect = list_rects[list_data.current]
    pygamelib.clamp_as_one(current_rect, list_rects, frame)

    running = True
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(display_size)
    # TODO
    # - per key repeat to disable only some keys
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
                    list_data.move(delta)
                    current_rect = list_rects[list_data.current]
                    pygamelib.clamp_as_one(current_rect, list_rects, frame)

        scroll_button_layout(scroll_button, list_data.current_proportion())
        screen.fill(background)
        list_renderer(screen, list_rects, current_rect, list_images, frame)

        contained = list_renderer.contained_items(frame, list_images, list_rects)
        if sum(1 for _ in contained) != sum(1 for _ in list_rects):
            scroll_button_renderer(screen, scroll_button)
        #scroll_frame_renderer(screen, scroll_frame)
        pygame.display.flip()
        elapsed = clock.tick(framerate)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        'words',
        nargs = '+',
        help = 'Words to populate listbox with.',
    )
    parser.add_argument(
        '--nshow',
        type = int,
        default = 5,
        help = 'Show %(dest)s items.',
    )
    args = parser.parse_args(argv)

    list_data = ListData(args.words, current=0)
    run(args.display_size, args.framerate, args.background, list_data, args.nshow)

if __name__ == '__main__':
    main()

# 2024-03-31 Sun.
# - listbox efforts pulled out of runegenerator.py
# - simplifying
# - cleanup
# - reusability
