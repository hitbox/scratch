import pygamelib

from pygamelib import pygame

def run(display_size, framerate, background, rects):
    clock = pygame.time.Clock()
    running = True
    font = pygamelib.monospace_font(20)
    screen = pygame.display.set_mode(display_size)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
        screen.fill(background)
        color = pygame.Color('red')
        color.a = 25
        # TODO
        # - rect.rect is silly
        for rect in rects:
            pygamelib.blit_rect(screen, rect.rect, color)
        pygame.display.flip()
        elapsed = clock.tick(framerate)

def main(argv=None):
    parser = pygamelib.command_line_parser()
    pygamelib.add_shapes_from_file_arguments(parser)
    pygamelib.add_seed_option(parser)
    args = parser.parse_args(argv)

    rects = list(pygamelib.shapes_from_args(args))

    run(args.display_size, args.framerate, args.background, rects)

if __name__ == '__main__':
    main()

# TODO
# - some way to render overlapping rects so they're all visible on screen
# - maybe order the rect by "how covered it is" with bottom-most rects brought
#   to the top (the end of the iterable)
