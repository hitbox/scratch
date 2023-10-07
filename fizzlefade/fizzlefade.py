import argparse
import os

from contextlib import redirect_stdout

with redirect_stdout(open(os.devnull, 'w')):
    import pygame

FRAMERATE = 60
FRAMERATE = 9999
WIDTH, HEIGHT = SIZE = (320, 200)

def iter_fizzlefade(size):
    """
    Randomly yield all pixel in 320x200 using linear-feedback shift register.
    """
    width, height = size
    random_value = 1
    while True:
        # low 8 bits
        y = (random_value & 0x000FF) - 1
        # high 9 bits
        x = (random_value & 0x1FF00) >> 8
        least_significant_bit = random_value & 0x00001
        random_value >>= 1
        if least_significant_bit == 0:
            # magic number specific to 320x200
            random_value ^= 0x00012000
        #if x < width and y < height:
        if 0 <= x < width and 0 <= y < height:
            yield (x, y)
        if random_value == 1:
            break

def test():
    """
    Test that `iter_fizzlefade` yields all pixels in 320x200.
    """
    pixels = set([(x,y) for y in range(HEIGHT) for x in range(WIDTH)])
    fizzlefade = iter_fizzlefade(SIZE)
    for pixel in fizzlefade:
        # fails with (0, -1)
        # why are we getting -1?
        pixels.remove(pixel)
    if not pixels:
        print('SUCCESS!')
    else:
        print('FAIL')

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args(argv)

    if args.test:
        test()
        return

    pygame.display.init()
    pygame.font.init()

    font = pygame.font.Font(None, 24)
    clock = pygame.time.Clock()
    fizzlefade = iter_fizzlefade(SIZE)

    scale = 4
    SCALED_SIZE = (WIDTH*scale, HEIGHT*scale + font.size('999')[1])
    display = pygame.display.set_mode(SCALED_SIZE)
    screen = pygame.Surface(SIZE)
    frame = screen.get_rect()

    running = True
    while running:
        elapsed = clock.tick(FRAMERATE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
        pos = next(fizzlefade)
        screen.set_at(pos, (200,10,10))
        text = f'{clock.get_fps():.2f}'
        image = font.render(text, True, (200,)*3, (0,)*3)
        screen.blit(image, image.get_rect(midbottom=frame.midbottom))
        pygame.transform.scale(screen, SCALED_SIZE, display)
        pygame.display.flip()

if __name__ == '__main__':
    main()
