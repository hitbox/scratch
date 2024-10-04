import random

import pygamelib

from pygamelib import pygame

def main(argv=None):
    default_side_size = 100

    parser = pygamelib.command_line_parser()
    parser.add_argument(
        '--rows',
        type = int,
        default = default_side_size,
    )
    parser.add_argument(
        '--cols',
        type = int,
        default = default_side_size,
    )
    args = parser.parse_args(argv)

    rows = args.rows
    cols = args.cols
    display_size = args.display_size

    side_size = 3
    deltas = pygamelib.deltas_for_size(side_size)
    deltas.remove((0,0))

    cells = {(i, j): 0 for i in range(cols) for j in range(rows)}

    clock = pygame.time.Clock()
    cells_image = pygame.Surface((rows, cols))

    for coord, cell in cells.items():
        if cell == 1:
            color = 'red'
            cells_image.set_at(coord, color)

    screen = pygame.display.set_mode(display_size)
    font = pygamelib.monospace_font(20)
    printer = pygamelib.FontPrinter(font, 'azure')

    cursor = None
    elapsed = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygamelib.post_quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                cellx, celly = (mouse_pos[0] // cols, mouse_pos[1] // rows)
                for dx, dy in deltas:
                    cells[cellx+dx, celly+dy] = 1
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                cellx, celly = (mouse_pos[0] // cols, mouse_pos[1] // rows)
                cursor = pygame.Rect((0,0), (10,10))
                cursor.center = (cellx, celly)
                # TODO
                # - properly scale cursor
                # - properly map coordinates from cell space to screen

        newcells = cells.copy()
        for (x, y), cell in cells.items():
            neighbor_coords = [(x+dx, y+dy) for (dx, dy) in deltas]
            neighbors = [cells[coord] for coord in neighbor_coords if coord in cells]
            living_neighbors = sum(neighbors)
            food_neighbors = sum(1 for cell in neighbors if cell == 0)
            if cell:
                # stay alive if between 3 and 7 livings neighbors, otherwise
                # die and become food.
                new_cell = int(2 < living_neighbors < 8)
            else:
                # become alive if more than 2 living neighbors and at least one
                # food
                new_cell = int(living_neighbors > 2 and food_neighbors > 0)
            newcells[(x, y)] = new_cell
            if new_cell:
                color = 'red'
            else:
                color = 'black'
            cells_image.set_at((x, y), color)
        cells = newcells

        screen.fill('black')
        pygame.transform.scale(cells_image, display_size, screen)
        lines = [
            f'FPS: {clock.get_fps():.0f}',
        ]
        image = printer(lines)
        screen.blit(image, (0,0))
        if cursor:
            pygame.draw.rect(screen, 'yellow', cursor, 1)
        pygame.display.flip()
        elapsed = clock.tick()

if __name__ == '__main__':
    main()

# https://www.reddit.com/r/pygame/comments/1fqo78p/discovered_a_cool_automaton/
# https://github.com/HLuksic/PyCells/
