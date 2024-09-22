import argparse
import math
import time as timelib

from time import time as system_time

import pygamelib

from pygamelib import pygame

K_DIGITS = set(getattr(pygame, f'K_{i}') for i in range(10))

K_FLOATS = K_DIGITS.union({pygame.K_UNDERSCORE, pygame.K_PERIOD})

def main(argv=None):
    parser = pygamelib.command_line_parser()
    args = parser.parse_args(argv)

    display = pygame.display.set_mode((900,)*2)
    window = display.get_rect()
    font = pygamelib.monospace_font(24)
    printer = pygamelib.FontPrinter(font, 'azure')
    clock = pygame.time.Clock()

    data = dict(
        frequency = 2, # Hz, cycles per second
        radius = window.centery // 2,
    )

    keys = {key[0]: key for key in data}

    selected_key = None
    entry = ''

    running = True
    while running:
        elapsed = clock.tick()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if selected_key:
                    if event.key == pygame.K_BACKSPACE:
                        entry = entry[:-1]
                    elif event.key == pygame.K_RETURN:
                        # commit
                        data[selected_key] = eval(entry)
                        entry = ''
                        selected_key = None
                    elif event.key == pygame.K_ESCAPE:
                        # abort
                        entry = ''
                        selected_key = None
                    else:
                        entry += event.unicode
                else:
                    if event.unicode.lower() in keys:
                        selected_key = keys[event.unicode.lower()]
                    elif event.key == pygame.K_ESCAPE:
                        pygamelib.post_quit()

        #
        time = system_time()
        pos = (
            window.centerx,
            window.centery + math.sin(math.tau * time * data['frequency']) * data['radius']
        )
        #
        display.fill('black')
        pygame.draw.circle(display, 'brown', pos, 10)
        lines = [
            f'FPS={clock.get_fps():0.2f}',
        ]
        for key, val in data.items():
            line = f'({key[0]}){key[1:]}={val}'
            if key == selected_key:
                line += f' >{entry}'
            lines.append(line)
        image = printer(lines)
        display.blit(image, image.get_rect(right=window.right))
        pygame.display.flip()

if __name__ == '__main__':
    main()
