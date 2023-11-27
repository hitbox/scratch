#!/usr/bin/env sh
set -euo pipefail
IFS=$'\n\t'

screen_size="(500,)*2"
draw_iterations="100"
rect_size="(250,)*2"
rect_color="'white'"

echo draw
echo
python -m timeit \
    --setup "import pygame" \
    --setup "screen = pygame.display.set_mode(${screen_size})" \
    --setup "rect = pygame.Rect((0,)*2, ${rect_size})" \
    --setup "rect.center = screen.get_rect().center" \
    -- \
    "for _ in range(${draw_iterations}):" \
    "    pygame.event.get()" \
    "    pygame.draw.rect(screen, ${rect_color}, rect)" \
    "    pygame.display.update()"

echo blit
echo
python -m timeit \
    --setup "import pygame" \
    --setup "screen = pygame.display.set_mode(${screen_size})" \
    --setup "image = pygame.Surface(${rect_size})" \
    --setup "image.fill(${rect_color})" \
    --setup "rect = image.get_rect(center=screen.get_rect().center)" \
    -- \
    "for _ in range(${draw_iterations}):" \
    "    pygame.event.get()" \
    "    screen.blit(image, rect)" \
    "    pygame.display.update()"
