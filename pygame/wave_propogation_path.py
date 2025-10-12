import argparse
import os

from contextlib import redirect_stdout

with redirect_stdout(open(os.devnull, 'w')):
    import pygame

CHARMAP = {
    'X': -1,
    ' ': 0,
}

NEIGHBOR_DELTAS = [
    (0, -1),
    (1, 0),
    (0, 1),
    (-1, 0),
]

def parse_text(lines):
    space = {}
    start = None
    dest = None
    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            if char == 'O':
                start = (x, y)
            elif char == 'D':
                dest = (x, y)
            space[(x, y)] = CHARMAP.get(char, 0)
    return start, dest, space

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('level')
    args = parser.parse_args(argv)

    with open(args.level, 'r') as level_file:
        start, dest, space = parse_text(level_file.readlines())

    stack = [start]
    cellw = 64
    cellh = 64
    width = cellw + max(x for x, y in space) * cellw
    height = cellh + max(y for x, y in space) * cellh
    screen = pygame.display.set_mode((width, height))
    world = screen.get_rect()
    clock = pygame.time.Clock()
    pygame.font.init()
    font = pygame.font.SysFont(None, 24)
    framerate = 60

    elapsed = 0
    current = None
    step = False
    step_countdown = 250
    step_timer = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, ):
                    step = True

        if stack and step:
            step = False
            nodex, nodey = current = stack.pop()
            space[current] += 1

            for x, y in NEIGHBOR_DELTAS:
                neighbor = (nodex + x, nodey + y)
                if neighbor in space and neighbor not in stack and space[neighbor] == 0:
                    space[neighbor] += space[current] + 1
                    stack.append(neighbor)

        # Draw
        maxval = max(space.values())
        if maxval == 0:
            maxval = cellw * cellh
        screen.fill('black')
        for point, value in space.items():
            x, y = point
            if value == -1:
                color = 'grey'
            else:
                color = pygame.Color('blue').lerp('red', value / maxval)
            topleft = (x*cellw, y*cellh)
            rect = pygame.Rect(topleft, (cellw, cellh))
            pygame.draw.rect(screen, color, rect, 0)
            if current and point == current:
                pygame.draw.rect(screen, 'black', rect, 8)

            image = font.render(f'{value}', True, 'white')
            screen.blit(image, image.get_rect(center=rect.center))

        texts = [f'{current=}', f'{(x, y)=}'] + [str(point) for point in stack]
        images = [font.render(text, True, 'red') for text in texts]
        rects = [image.get_rect() for image in images]
        if rects:
            rects[0].bottomleft = world.bottomleft
            for r1, r2 in zip(rects, rects[1:]):
                r2.bottomleft = r1.topleft

        for image, rect in zip(images, rects):
            screen.blit(image, rect)

        pygame.display.flip()
        elapsed = clock.tick(framerate)
        step_timer += elapsed
        if step_timer > step_countdown:
            step = True
            step_timer = 0

if __name__ == '__main__':
    main()
