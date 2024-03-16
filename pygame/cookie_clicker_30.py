import math
import pygame

score = time = 0
pygame.font.init()
font = pygame.font.SysFont('monospace', 50)
clock = pygame.time.Clock()
screen = pygame.display.set_mode((900,)*2)
cookie = ((450,)*2, 200)
pygame.draw.circle(screen, 'saddlebrown', cookie[0], cookie[1], 0)

while not pygame.event.peek(pygame.QUIT):
    if (events := pygame.event.get(pygame.MOUSEBUTTONDOWN)) and math.dist(events[0].pos, cookie[0]) < cookie[1]:
        score += 1
    time += clock.tick(60)
    screen.blit(font.render(f'time={time//1000}', True, 'white', 'black'), (350,0))
    screen.blit(font.render(f'{score=}', True, 'white', 'saddlebrown'), (350,425))
    pygame.display.flip()

# 2024-03-15 Fri.
# Cookie Clicker in 30 lines
# https://www.youtube.com/watch?v=5C7squ2nCQw
# https://gist.github.com/hitbox/08574ab7598f8b94a2eadaf4d1db6d4f
# - copy this code to the gist minus comments at bottom
