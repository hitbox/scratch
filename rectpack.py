import argparse
import contextlib
import os
import random

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

class RectPack:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.reset()

    def reset(self):
        self.grid = [0 for _ in range(self.width)]

    def insert(self, width, height):
        # faithful implementation of original
        # favors the start of the space
        best_x = 0
        best_y = self.height - height + 1

        for x in range(self.width - width):
            cy = self.grid[x]
            is_best = True
            for bx in range(x, x + width):
                if self.grid[bx] > best_y:
                    is_best = False
                    x = bx
                    break
                if self.grid[bx] > cy:
                    cy = self.grid[bx]
            if is_best:
                best_x = x
                best_y = cy

        if best_y + height < self.height:
            for x in range(best_x, best_x + width):
                self.grid[x] = best_y + height
            return (best_x, best_y)


def run(width, height, factor):
    rectpack = RectPack(width, height)

    screen = pygame.display.set_mode((width, height))

    colors = [
        name for name in pygame.color.THECOLORS
        if 'black' not in name
        and 'white' not in name
        and 'grey' not in name
        and 'gray' not in name
    ]

    def random_pack():
        screen.fill('black')
        rectpack.reset()
        while True:
            w = random.randint(1, rectpack.width / factor)
            h = random.randint(1, rectpack.height / factor)
            position = rectpack.insert(w, h)
            if not position:
                break
            x, y = position
            rect = pygame.Rect(x, y, w, h)
            color = random.choice(colors)
            pygame.draw.rect(screen, color, rect)
        pygame.display.flip()

    random_pack()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                else:
                    random_pack()

def main(argv=None):
    """
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('width', type=int)
    parser.add_argument('height', type=int)
    parser.add_argument('--factor', type=int, default=32)
    args = parser.parse_args()
    run(args.width, args.height, args.factor)

if __name__ == '__main__':
    main()

# 2023-10-07
# - cleaning up my github projects
# - duplicates of the effort to make ZType in Python/pygame.
# - ZType was made by guy who made this:
#   https://github.com/phoboslab/rectpack/blob/master/rectpack.js
# - It has the feel of a constraint resolver--a purpose built one.
# - After intial rewrite ideas:
#   - collect/pack rects by shared-size sides?
#   - if so, favor horizontal or vertical?
