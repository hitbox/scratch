import pygamelib

from pygamelib import pygame

def main(argv=None):
    parser = pygamelib.command_line_parser()
    args = parser.parse_args(argv)

    clock = pygame.time.Clock()
    gui_font = pygamelib.monospace_font(30)
    point_font = pygamelib.monospace_font(15)
    printer = pygamelib.FontPrinter(gui_font, 'azure')
    screen = pygame.display.set_mode(args.display_size)
    window = screen.get_rect()

    width = window.width * 0.50
    line_rect = pygame.Rect(0, 0, width, window.height)
    line_rect.center = window.center

    a, b = map(pygame.Vector2, (line_rect.midleft, line_rect.midright))
    line = (a, b)

    radius = 5
    elapsed = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
        mouse_position = pygame.mouse.get_pos()

        screen.fill('black')
        for point, attr in zip(line, ['midright', 'midleft']):
            image = point_font.render(str(point), True, 'azure')
            rect = image.get_rect(**{attr: point})
            screen.blit(image, rect)
        pygame.draw.line(screen, 'steelblue4', line[0], line[1])
        # Circle on line at mouse position.
        mouse_line_point = (mouse_position[0], line[0][1])
        pygame.draw.circle(screen, 'goldenrod', mouse_line_point, radius)
        # Coordinates text of point on line
        image = point_font.render(str(mouse_line_point), True, 'crimson')
        rect = image.get_rect(midtop=(mouse_line_point[0], mouse_line_point[1] + radius * 4))
        screen.blit(image, rect)
        # Time of point on line.
        time = pygamelib.inverse_lerp(a, b, mouse_line_point)
        image = point_font.render(f'{time=:.4f}', True, 'azure')
        rect = image.get_rect(midbottom=(mouse_line_point[0], mouse_line_point[1] - radius * 4))
        screen.blit(image, rect)

        # Debugging.
        screen.blit(image, rect)
        lines = [
            f'FPS: {clock.get_fps():.0f}',
        ]
        image = printer(lines)
        screen.blit(image, (0,0))
        pygame.display.flip()
        elapsed = clock.tick()

if __name__ == '__main__':
    main()
