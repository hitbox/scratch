import argparse

import pygame

def generate_gradient_border_surface(width, height, border_width, color1, color2):
    # get a 3x3 surface, setting gradient colors
    surface = pygame.Surface((3, 3))
    pixarr = pygame.PixelArray(surface)
    corners = [(0,0), (0, 2), (2, 0), (2, 2)]
    for x, y in corners:
        pixarr[x, y] = color1
        sides = [(0, 1), (2, 1), (1, 0), (1, 2)]
        for x, y in sides:
            pixarr[x, y] = color2
    # stretch the surface to get gradient
    surface = pygame.transform.smoothscale(surface, (width, height))
    # fill the inner rect to get gradient border
    background = pygame.Surface((width - 2*border_width, height - 2*border_width))
    background.fill('black')
    surface.blit(background, [border_width]*2)
    surface.set_colorkey('black')

    return surface

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('check', type=int)
    args = parser.parse_args(argv)

    resolution = (500, 300)
    pygame.init()
    screen = pygame.display.set_mode(resolution)

    color_corners = pygame.Color('red')
    color_sides = pygame.Color('green')
    surface = generate_gradient_border_surface(300, 200, 5, color_corners, color_sides)

    if args.check:
        screen.fill((100, 50, 70))
    else:
        screen.fill('palevioletred4')
    screen.blit(surface, (50, 50))
    pygame.display.flip()
    while not pygame.event.peek(pygame.QUIT):
        pass

if __name__ == '__main__':
    main()

# 2024-02-13 Tue.
# https://www.reddit.com/r/pygame/comments/1apvvh1/a_huge_thanks_to_itah_pygame_member_who_showed_me/
