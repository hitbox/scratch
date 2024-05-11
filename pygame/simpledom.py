import argparse

import pygamelib

from pygamelib import pygame

class DOMElement:

    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))


class TextElement(DOMElement):

    def __init__(self, x, y, text, font_size, color):
        super().__init__(x, y, 0, 0, color)
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.render_text()

    def render_text(self):
        self.image = self.font.render(self.text, True, self.color)
        self.width, self.height = self.image.get_size()

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)

    pygame.font.init()
    rectangle = DOMElement(100, 100, 200, 100, 'red')
    text = TextElement(200, 300, "Hello, Pygame!", font_size=30, color='white')

    screen = pygame.display.set_mode((800, 600))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw elements
        screen.fill('black')  # Fill screen with black color
        rectangle.draw(screen)
        text.draw(screen)

        pygame.display.flip()

if __name__ == '__main__':
    main()
