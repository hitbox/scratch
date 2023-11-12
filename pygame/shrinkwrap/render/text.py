from lib.external import pygame

def lines(font, antialias, color, lines, surface_flags=0):
    """
    Render lines of text.

    :param font: pygame Font instance.
    :param antialias: bool to antialias.
    :param color: font.render color.
    :param lines: iterable of strings.
    :param surface_flags: pygame.Surface flags argument for new surface.
    """
    # thinking it's a good idea not to engineer another function to assemble
    # the rects. this is another simple pattern that's easy to do and keep this
    # function self contained.
    images = [font.render(line, antialias, color) for line in lines]
    rects = [image.get_rect() for image in images]
    for r1, r2 in zip(rects[:-1], rects[1:]):
        r2.top = r1.bottom
    width = max(rect.right for rect in rects)
    height = sum(rect.height for rect in rects)
    surf = pygame.Surface((width, height), flags=surface_flags)
    for rect, image in zip(rects, images):
        surf.blit(image, rect)
    return surf
