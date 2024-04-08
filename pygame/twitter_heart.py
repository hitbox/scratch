import pygamelib

from pygamelib import pygame

def main(argv=None):
    parser = pygamelib.command_line_parser()
    parser.add_argument(
        'inside',
        type = pygamelib.rect_type(with_pygame=True),
        help = 'Draw heart inside rect.',
    )
    args = parser.parse_args(argv)

    display_size = args.display_size
    framerate = args.framerate
    background = args.background
    inside = args.inside

    window = pygamelib.make_rect(size=display_size)

    heart = pygamelib.HeartShape2(
        cleft_angle = 45,
        inside = inside,
    )

    color = pygamelib.get_color('white', a=127)
    debug_color = pygamelib.get_color('red', a=127)

    elapsed = 0
    running = True
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(window.size)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
        screen.fill(background)
        pygame.draw.rect(screen, 'grey20', inside, 1)
        heart.draw(screen, color, 1, debug_color=debug_color)
        pygame.display.flip()
        elapsed = clock.tick(framerate)

if __name__ == '__main__':
    main()

# 2024-04-08 Mon.
# Make the twitter heart clicked animation with pygame
# - Eclipse day
# - https://css-tricks.com/recreating-the-twitter-heart-animation/
# - https://codepen.io/thebabydino/pen/RRRRZE?editors=1100
# TODO
# - fit heart to bounding rect
# - scalable heart shape
# - exploding circle animation
# - particles
# - styling
