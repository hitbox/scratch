import argparse
import contextlib
import itertools as it
import operator as op
import os

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

sides = op.attrgetter('top', 'right', 'bottom', 'left')

def rect_from_points(x1, y1, x2, y2):
    w = x2 - x1
    h = y2 - y1
    return (x1, y1, w, h)

def aggsides(func, *rects):
    return map(func, *map(sides, rects))

def minsides(*rects):
    return aggsides(min, *rects)

def maxsides(*rects):
    return aggsides(max, *rects)

def iter_rect_diffs(rect, inside):
    _, minright, minbottom, _ = minsides(rect, inside)
    maxtop, _, _, maxleft = maxsides(rect, inside)
    # topleft
    yield rect_from_points(*inside.topleft, *rect.topleft)
    # top
    yield rect_from_points(maxleft, inside.top, minright, rect.top)
    # topright
    yield rect_from_points(minright, inside.top, inside.right, rect.top)
    # right
    yield rect_from_points(minright, maxtop, inside.right, minbottom)
    # bottomright
    yield rect_from_points(*rect.bottomright, *inside.bottomright)
    # bottom
    yield rect_from_points(maxleft, rect.bottom, minright, inside.bottom)
    # bottomleft
    yield rect_from_points(inside.left, rect.bottom, rect.left, inside.bottom)
    # left
    yield rect_from_points(inside.left, maxtop, rect.left, minbottom)

def validate_inside(rect, inside):
    _, _, w, h = rect
    return 0 < w < inside.width and 0 < h < inside.height

def margin_rects(rects, inside):
    for rect in rects:
        for other in iter_rect_diffs(rect, inside):
            yield other

def area(rect):
    return rect.width * rect.height

def run():
    pygame.font.init()
    width = 300
    height = 200
    scale = 4
    screen = pygame.display.set_mode((width*scale, height*scale))
    buffer = pygame.Surface((width, height))
    window = buffer.get_rect()
    clock = pygame.time.Clock()
    framerate = 60
    font = pygame.font.SysFont('monospace', 12)
    space = window.inflate((-min(window.size)//3,)*2)
    colors = [
        'brown',
        'olive',
        'orchid',
        'orange',
        'turquoise',
        'purple',
        'salmon',
        'olivedrab',
        'teal',
    ]
    refrect = space.inflate((-min(space.size)//1.25,)*2)
    refrect.normalize()
    draggables = [refrect.copy()]

    dragging = None
    running = True
    while running:
        margins = map(
            pygame.Rect,
            filter(
                lambda other: validate_inside(other, space),
                margin_rects(draggables, space)
            )
        )
        # create labels
        text_blits = []
        for rect, color in zip(margins, colors):
            pygame.draw.rect(buffer, color, rect, 1)
            text = f'{rect.width}x{rect.height}={rect.width*rect.height}'
            image = font.render(text, True, 'azure')
            rect = image.get_rect(center=rect.center)
            text_blits.append((image, rect))
        # separate text labels
        while True:
            rects = list(rect for _, rect in text_blits)
            if not any(r1.colliderect(r2) for r1, r2 in it.combinations(rects, 2)):
                break
            for r1, r2 in it.combinations(rects, 2):
                if r1.colliderect(r2):
                    overlap = pygame.Vector2(r1.clip(r2).size)
                    r1.topleft -= overlap / 2
                    r2.topleft += overlap / 2
                    # TODO
                    # - also constrain to window
        # drawing
        buffer.fill('black')
        # draw draggables
        for rect in draggables:
            pygame.draw.rect(buffer, 'purple4', rect, 1)
        # draw text labels
        for (image, rect), color in zip(text_blits, colors):
            pygame.draw.circle(buffer, color, rect.center, 2)
            buffer.blit(image, rect)
        # scale and update display
        pygame.transform.scale(buffer, (width*scale, height*scale), screen)
        pygame.display.flip()
        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                world_pos = map(lambda x: x / scale, event.pos)
                for rect in draggables:
                    if rect.collidepoint(*world_pos):
                        dragging = rect
                        break
                else:
                    dragging = None
            elif event.type == pygame.MOUSEMOTION and event.buttons[0] and dragging:
                # left button down and moving
                delta = pygame.Vector2(*map(lambda x: x / scale, event.rel))
                # validate new position for margin area size
                testrect = pygame.Rect(dragging.topleft + delta, dragging.size)
                _margins = map(pygame.Rect, margin_rects([testrect], space))
                # all areas > x and there are valid margin rects all around
                valid_move = all(
                    validate_inside(rect, space) and area(rect) > 1000
                    for rect in _margins
                )
                if valid_move:
                    dragging.topleft += delta
        clock.tick(framerate)

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)
    run()

if __name__ == '__main__':
    main()
