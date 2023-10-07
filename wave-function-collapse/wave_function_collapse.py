import argparse
import contextlib
import os

from collections import Counter
from itertools import product

with contextlib.redirect_stdout(open(os.devnull,'w')):
    import pygame

def get_tiles(input_image, size):
    """
    Slide over `input_image` obtaining squares of side size `size`, wrapping
    around edges.
    """
    output = []
    input_width, input_height = input_image.get_size()
    for y, x in product(range(input_height), range(input_width)):
        surface = pygame.Surface((size,)*2)
        for offx, offy in product(range(size), repeat=2):
            source = ((x+offx) % input_width, (y+offy) % input_height)
            color = input_image.get_at(source)
            surface.set_at((offx, offy), color)
        output.append(surface)
    return output

def get_surface_table(surf):
    """
    Return nested tuple table of the colors of a surface.
    """
    width, height = surf.get_size()
    table = tuple(
        tuple(
            tuple(surf.get_at((x,y))) for x in range(width)
        )
        for y in range(height)
    )
    return table

def sample_input_image(size, color, background):
    """
    Produce a sample input image like the one on gridbugs.org.
    """
    # the first 4x4 input image generator
    # https://www.gridbugs.org/wave-function-collapse/
    rect = pygame.Rect((0,0), size)
    surface = pygame.Surface(size, flags=pygame.SRCALPHA)
    surface.fill(background)
    pygame.draw.line(surface, color, (1,rect.top), (1,rect.bottom), 1)
    pygame.draw.line(surface, color, (rect.left,rect.bottom-2), (rect.right,rect.bottom-2), 1)
    return surface

def post_quit():
    pygame.event.post(pygame.event.Event(pygame.QUIT))

def main(argv=None):
    """
    Wave function collapse in pygame
    """
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

    pygame.display.init()
    screen = pygame.display.set_mode((800,800))
    buffer = pygame.Surface((100,100))
    frame = buffer.get_rect()
    clock = pygame.time.Clock()

    sample = sample_input_image((4,8), (200,)*3, (0,)*3)
    output = get_tiles(sample, 3)

    # index aligned
    table_surface_map = dict((get_surface_table(surf), surf) for surf in output)
    # inserting keys into the dict will have made the values unique.
    unique_tiles = list(table_surface_map.values())

    # NOTE
    # 2022-01-05:
    #   Left off here. The tiles of the input image are "rules" for what pixels
    #   may be drawn in the output image. How the rules are applied is not well
    #   understood. Since pygame Surface objects aren't hashable mapping and
    #   counting and finding unique tiles is difficult.
    # 2022-01-07:
    #   * think this being called wave function collapse is silly. it's just
    #     rules for placing tiles.

    # count dupes
    counter = Counter(table_surface_map.keys())

    # display input image
    buffer.fill((40,)*3)
    rect = sample.get_rect(center=frame.center)
    buffer.blit(sample, rect)

    # display tiles
    print(f'{len(output)=}')
    x = y = 2
    for surf in output:
        buffer.blit(surf, (x, y))
        if surf.get_rect(x=x,y=y).right > frame.centerx // 4:
            y += surf.get_height() + 2
            x = 2
        else:
            x += surf.get_width() + 2

    pygame.transform.scale(buffer, (800,)*2, screen)

    running = True
    while running:
        elapsed = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    post_quit()
        pygame.display.update()

if __name__ == '__main__':
    main()
