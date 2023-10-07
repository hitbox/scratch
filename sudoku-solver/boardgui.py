import argparse
import math
import os

from contextlib import redirect_stdout

import sudoku

with redirect_stdout(open(os.devnull, 'w')):
    import pygame

FRAMERATE = 60
NUMBERS = set(range(1,10))

def wraprect(rects):
    """
    Return rect that wraps given rects.
    """
    left = min(rect.left for rect in rects)
    top = min(rect.top for rect in rects)
    right = max(rect.right for rect in rects)
    bottom = max(rect.bottom for rect in rects)
    return pygame.Rect(left, top, right - left, bottom - top)

def moveclamp(inside, rects, padding=0):
    """
    Clamp, moving, sprites to frame as group
    """
    wrapped = wraprect(rects).inflate(padding, padding)
    if not inside.contains(wrapped):
        moved = wrapped.clamp(inside)
        dx = moved.x - wrapped.x
        dy = moved.y - wrapped.y
        for rect in rects:
            rect.x += dx
            rect.y += dy

def wrapclamp(inside, rects):
    """
    Move rects from topleft to bottomright wrapping.
    """
    last = None
    for rect in rects:
        if last is None:
            rect.topleft = inside.topleft
        else:
            rect.topleft = last.topright
        if not inside.contains(rect):
            rect.left = inside.left
            rect.top = rect.bottom
        last = rect

def render_cell(font, cell_size, square, num=None):
    surf = pygame.Surface((cell_size,)*2)
    if square % 2 == 0:
        surf.fill((125,125,150))
    if num:
        text = font.render(f'{num}', True, (200,)*3)
    pygame.draw.rect(surf, (200,)*3, surf.get_rect(), 1)
    return surf

def render_circle(size, color, background=None, width=1):
    image = pygame.Surface((size,)*2, flags=pygame.SRCALPHA)
    rect = image.get_rect()
    radius = size // 2
    if background is not None:
        pygame.draw.circle(image, background, rect.center, radius)
    pygame.draw.circle(image, color, rect.center, radius, width)
    return image

def populate_menu_wheel(font, group, prompt, frame, cell):
    """
    Fill a group with sprites for option wheel.
    """
    spread_angle = math.tau / len(prompt)
    radius = 85
    cx, cy = cell.rect.center
    for index, num in enumerate(sorted(prompt)):
        sprite = pygame.sprite.Sprite(group)
        sprite.num = num
        sprite.board_index = cell.board_index
        text = font.render(f'{num}', True, (200,)*3)
        size = max(text.get_size()) * 2
        sprite.image = render_circle(size, (200,)*3, (10,)*3)
        # XXX
        # * left off here trying to clean up the code with functions
        # * need nicer way of handling what gets the events for clicking and
        #   mouse motions and such
        sprite.rect = sprite.image.get_rect()
        sprite.image.blit(text, text.get_rect(center=sprite.rect.center))
        sprite.rect.centerx = cx + math.cos(index * spread_angle) * radius
        sprite.rect.centery = cy + math.sin(index * spread_angle) * radius
    moveclamp(frame, [sprite.rect for sprite in group], padding=20)

def populate_cells_group(cells_group, frame, font):
    cells_frame_size = min(frame.size) - .1 * min(frame.size)
    cells_frame_rect = pygame.Rect((0,0), (cells_frame_size,)*2)
    cells_frame_rect.center = frame.center
    cell_size = cells_frame_size // 9

    # sudoku boards cells to put numbers on
    for index in range(9*9):
        (row,col), (sqrow,sqcol), square = sudoku.cellinfo(index)
        cell_sprite = pygame.sprite.Sprite(cells_group)
        cell_sprite.board_index = index
        cell_sprite.num = 0
        cell_sprite.image = render_cell(font, cell_size, square)
        cell_sprite.rect = cell_sprite.image.get_rect()
    wrapclamp(cells_frame_rect, [sprite.rect for sprite in cells_group])

def loop(board):
    pygame.display.init()
    pygame.font.init()

    screen = pygame.display.set_mode((800,800))
    frame = screen.get_rect()
    background = screen.copy()
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 40)

    cells_group = pygame.sprite.Group()
    populate_cells_group(cells_group, frame, font)

    # NOTES:
    # * looks like a stack for current "thing" that should consume events would
    #   be good.
    prompt_group = pygame.sprite.Group()
    active = cells_group
    running = True
    hover = None
    prompt = None
    while running:
        elapsed = clock.tick(FRAMERATE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.type == pygame.MOUSEMOTION:
                # Hover
                if active:
                    for sprite in active:
                        if sprite.rect.collidepoint(event.pos):
                            hover = sprite
                            break
                    else:
                        hover = None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Click
                if cells_group.has(hover):
                    # number prompt wheel
                    prompt = sudoku.possible_numbers(board, hover.board_index)
                    if hover.num != 0:
                        prompt.add(0)
                    if prompt:
                        prompt_group.empty()
                        populate_menu_wheel(font, prompt_group, prompt, frame, hover)
                        hover = None
                        active = prompt_group

                elif prompt_group.has(hover):
                    # clicked number to put in cell
                    index = hover.board_index
                    (row,col), (sqrow,sqcol), square = sudoku.cellinfo(index)
                    for sprite in cells_group:
                        if sprite.board_index == index:
                            sprite.num = hover.num
                            if hover.num == 0:
                                cell_sprite.image = pygame.Surface((cell_size,)*2)
                                if square % 2 == 0:
                                    cell_sprite.image.fill((125,125,150))
                                pygame.draw.rect(cell_sprite.image, (200,)*3,
                                        cell_sprite.image.get_rect(), 1)
                            else:
                                text = font.render(f'{hover.num}', True, (200,)*3)
                                pos = text.get_rect(center=sprite.image.get_rect().center)
                                sprite.image.blit(text, pos)
                            board[row][col] = hover.num
                            break
                    prompt_group.empty()
                    hover = None
                    active = cells_group

                else:
                    prompt_group.empty()
                    hover = None
                    active = cells_group

        # draw - clear
        screen.blit(background, (0, 0))
        cells_group.draw(screen)
        prompt_group.draw(screen)
        if hover is not None:
            pygame.draw.rect(screen, (200,200,100), hover.rect, 4)
        pygame.display.update()

def main(argv=None):
    """
    Manually fill sudoku board.
    """
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)
    board = [ [0 for _ in range(9)] for _ in range(9) ]
    loop(board)

if __name__ == '__main__':
    main()
