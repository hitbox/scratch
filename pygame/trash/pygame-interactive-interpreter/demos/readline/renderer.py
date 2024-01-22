from lib.external import pygame
from lib.rect import wraprects

class ReadlineRenderer:
    """
    Create images from readline character buffer.
    """

    def __init__(self, font):
        self.font = font

    def render(self, readline, inside):
        """
        :param readline: lib.Readline instance
        :param inside: rect to keep render inside
        """
        items = []
        # render characters highlighting the cursor
        # wrapping and left-to-right position is done with the previous rect
        inside = inside.copy()
        inside.topleft = (0, 0)
        rect = pygame.Rect(0,0,0,0)
        for index, char in enumerate(readline.buffer):
            if index == readline.cursor:
                foreground = (10,)*3
                background = (200,)*3
            elif char == ' ':
                foreground = (200,)*3
                background = (30,)*3
            else:
                foreground = (200,)*3
                background = None
            if background:
                image = self.font.render(char, True, foreground, background)
            else:
                image = self.font.render(char, True, foreground)
            # position
            kwargs = dict(left = rect.right, top=rect.top)
            if not inside.contains(image.get_rect(**kwargs)):
                # position top to bottom and the normal condition top=top takes
                # care of keeping new vertical position.
                kwargs['top'] = rect.bottom
                kwargs['left'] = inside.left
            rect = image.get_rect(**kwargs)
            items.append((image, rect))
        # render cursor if at end
        if readline.cursor >= len(readline.buffer):
            background = pygame.Surface(self.font.size(' '))
            background.fill((200,)*3)
            rect = background.get_rect(left = rect.right, top=rect.top)
            items.append((background, rect))
        # assemble the images and rects
        rect = wraprects(rect for image, rect in items)
        result = pygame.Surface(rect.size, pygame.SRCALPHA)
        for image, rect in items:
            result.blit(image, rect)
        return result
