import argparse
import contextlib
import itertools as it
import os

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

def resolve_overlaps(movable_rects, immovable_rects):
    for rect1, rect2 in it.combinations(movable_rects, 2):
        if (
            not rect1.colliderect(rect2)
            or
            rect1 in immovable_rects
            and
            rect2 in immovable_rects
        ):
            continue
        elif rect1 in immovable_rects:
            resolve_overlap(rect2, rect1)
        elif rect2 in immovable_rects:
            resolve_overlap(rect1, rect2)
        else:
            # Move both rectangles away from each other
            delta = pygame.Vector2(rect1.center) - rect2.center
            if delta:
                delta.normalize_ip()
                rect1.center += delta
                rect2.center -= delta

def resolve_overlap(rect, immovable):
    overlap = rect.clip(immovable)
    if overlap.width > 0 and overlap.height > 0:
        dx = overlap.width
        dy = overlap.height
        if dx < dy:
            if rect.centerx < immovable.centerx:
                rect.right = immovable.left
            else:
                rect.left = immovable.right
        else:
            if rect.centery < immovable.centery:
                rect.bottom = immovable.top
            else:
                rect.top = immovable.bottom

def run():
    width = 800
    height = 600
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    movable_rects = [
        pygame.Rect(250, 200, 100, 100),
        pygame.Rect(300, 150, 100, 100), # pinned
        pygame.Rect(250, 400, 100, 100),
        pygame.Rect(300, 410, 100, 100),
    ]

    immovable_rects = [
        pygame.Rect(300, 150, 100, 100), # pinned
    ]

    resolve_timer = 0
    resolve_every = 250
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
        screen.fill('black')
        for rect in movable_rects:
            pygame.draw.rect(screen, 'blue', rect, 1)
        for rect in immovable_rects:
            pygame.draw.rect(screen, 'red', rect, 1)
        pygame.display.flip()
        elapsed = clock.tick(60)
        if resolve_timer + elapsed >= resolve_every:
            resolve_timer = (resolve_timer + elapsed) % resolve_every
            resolve_overlaps(movable_rects, immovable_rects)
        else:
            resolve_timer += elapsed

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)
    run()

if __name__ == '__main__':
    main()
