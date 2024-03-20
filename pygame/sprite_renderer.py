import math

import pygamelib

from pygamelib import pygame

class Node:

    def __init__(self, parent, children, data):
        self.parent = parent
        self.children = children
        self.data = data


# XXX: THINKING
# - push attributes down through nodes
# - adding them together
# - renderer receives them like a context and has defaults
# - kind of want ChainMap with addition

def run(display_size, framerate):
    clock = pygame.time.Clock()
    window = pygame.Rect((0,0), display_size)
    running = True
    screen = pygame.display.set_mode(window.size)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
        elapsed = clock.tick(framerate)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument('nodes', nargs='+')
    args = parser.parse_args(argv)

    root = Node(parent=None)
    root.rotation = math.tau / 4
    root.scale = 2

    some_node = Node(parent=root)

    print(args)
    return
    run(args.display_size, args.framerate)

if __name__ == '__main__':
    main()
