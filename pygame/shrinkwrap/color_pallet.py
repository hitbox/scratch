import argparse
import contextlib
import os

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

from pygame.color import THECOLORS

def value(color):
    return pygame.Color(color).hsva[2]

GRAY = (color for name, color in THECOLORS.items() if name.startswith('gray'))
GRAY = sorted(GRAY, key=value)

def most_square_ncols(numitems):
    """
    Find the number of columns for numitems that results in the most square
    number of rows.
    """
    def rowcoldiff(ncols):
        nrows = sum(divmod(numitems, ncols))
        r = abs(1 - (nrows / ncols))
        print(r)
        return r

    return min(range(1, numitems), key=rowcoldiff)

def main(argv=None):
    """
    """
    parser = argparse.ArgumentParser(
        description = main.__doc__,
    )
    args = parser.parse_args(argv)

    colors = GRAY

    # TODO: how to make a square from N?
    height, width = divmod(len(colors), 2)

    pallet_image = pygame.Surface((width, height))
    pallet_rect = pallet_image.get_rect()

    for index, color in enumerate(colors):
        y, x = divmod(index, side_length)
        pos = (x, y)
        #print(pos)
        pallet_image.set_at(pos, color)

    SIDE = 16
    SCALE = 50
    WINDOWSIZE = (800,)*2

    pygame.display.init()

    image = pygame.Surface((SIDE,)*2)
    rect = image.get_rect()

    window = pygame.display.set_mode(WINDOWSIZE)
    frame = window.get_rect()

    current_color = None
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.type == pygame.MOUSEMOTION:
                current_color = window.get_at(event.pos)
        # draw
        #image.blit(pallet_image, pallet_image.get_rect(center=rect.center))
        window.fill((40,20,40))
        #window.blit(pallet_image, pallet_image.get_rect(center=frame.center))
        size = tuple(map(int, map(lambda v: v*48, pallet_rect.size)))
        image = pygame.transform.scale(pallet_image, size)
        window.blit(image, image.get_rect(center=frame.center))
        if current_color:
            pygame.draw.rect(window, current_color, pygame.Rect(frame.right - 100, frame.top, 100, 100))
        pygame.display.flip()


if __name__ == '__main__':
    main()
