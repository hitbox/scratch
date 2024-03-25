import pygamelib

from pygamelib import pygame

def run(display_size, framerate, background):
    clock = pygame.time.Clock()
    running = True
    screen = pygame.display.set_mode(display_size)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        elapsed = clock.tick(framerate)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    args = parser.parse_args(argv)
    run(args.display_size, args.framerate, args.background)

if __name__ == '__main__':
    main()

# Date
# Notes about why this is and what it does
